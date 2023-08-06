import time
from datetime import datetime
import numpy as np
from scipy.integrate import solve_ivp
from tqdm import tqdm


class Simulation:
    """
    Class that wraps simulation solver. currently only solve_ivp.

    Attributes
    ----------
          time :  ndarray
               Not unique tag that will be used in reports or printed output.
          delta_t :  float
               timestep.
          callbacks :  list
               Not unique tag that will be used in reports or printed output.
          model :
               Not unique tag that will be used in reports or printed output.
    """

    def __init__(self, model, t_start=0, t_stop=20000, num=1000, num_inner=1, max_event_steps=100,
                 start_datetime=datetime.now(), **kwargs):
        """
            Creating a namespace.

            Parameters
            ----------
            tag : string
                Name of a `VariableNamespace`

            Returns
            -------
            new_namespace : `VariableNamespace`
                Empty namespace with given name
        """

        self.time, self.delta_t = np.linspace(t_start, t_stop, num + 1, retstep=True)
        self.callbacks = []
        #self.recent_scope = None
        self.async_callback = []
        self.model = model
        self.start_datetime = start_datetime
        self.num_inner = num_inner
        self.options = kwargs
        self.max_event_steps = max_event_steps
        self.info = model.info["Solver"]
        self.info["Number of Equation Calls"] = 0
        self.y0 = [y for y, _ in [(x.get_value(), x.update_ix(i)) for i, x in enumerate(self.model.states.values())]]
        self.events = [model.events[event_name].event_function._event_wrapper() for event_name in model.events]
        self.callbacks = [x.callbacks for x in model.callbacks]
        self.t_scope = self.model._get_initial_scope_copy()

    def __end_step(self, y, t, event_id=None, **kwargs):
        self.model._update_scope_states(y)
        self.t_scope.update_model_from_scope(self.model)
        for callback in self.callbacks:
            callback(t, self.model.path_variables, **kwargs)
        if event_id is not None:
            list(self.model.events.items())[event_id][1]._callbacks_call(t, self.model.path_variables)

        self.model.sychronize_scope()
        self.y0 = self.model.states_as_vector

    def __init_step(self):
        [x.initialize(simulation=self) for x in self.model.callbacks]


    def solve(self):
        """
        solve the model.

        Returns
        -------
        Solution : 'OdeSoulution'
                returns the most recent OdeSolution from scipy

        """

        self.__init_step() # initialize

        result_status = "Success"
        stop_condition = False
        sol = None
        event_steps = 0
        try:
            for t in tqdm(self.time[0:-1]):
                step_not_finished = True
                current_timestamp = t
                while step_not_finished:
                    t_eval = np.linspace(current_timestamp, t + self.delta_t, self.num_inner + 1)

                    sol = solve_ivp(self.__func, (current_timestamp, t + self.delta_t), y0=self.y0, t_eval=t_eval,
                                    events=self.events, dense_output=True,
                                    **self.options)
                    step_not_finished = False
                    event_step = sol.status == 1

                    if sol.status == 0:
                        current_timestamp = t + self.delta_t
                    if event_step:
                        event_id = np.nonzero([x.size > 0 for x in sol.t_events])[0][0]
                        # solution stuck
                        stop_condition = False
                        if (abs(sol.t_events[event_id][0] - current_timestamp) < 1e-6):
                            event_steps += 1
                        else:
                            event_steps = 0

                        if event_steps > self.max_event_steps:
                            stop_condition = True
                        current_timestamp = sol.t_events[event_id][0]

                        step_not_finished = True

                        self.__end_step(sol.sol(current_timestamp), current_timestamp, event_id=event_id)
                    else:
                        if sol.success:
                            self.__end_step(sol.y[:, -1], current_timestamp)
                        else:
                            result_status = sol.message
                    if stop_condition:
                        break
                if stop_condition:
                    result_status = "Stopping condition reached"
                    break
            #time.sleep(1)
        except Exception as e:
            raise e
        finally:
            self.info.update({"Solving status": result_status})
            list(map(lambda x: x.finalize(), self.model.callbacks))
        return sol

    def __func(self, _t, y):

        self.t_scope.update_states(y)
        list(map(lambda x: x.set_time(_t), self.t_scope.scope_dict.values()))
        self.info["Number of Equation Calls"] = self.info["Number of Equation Calls"] + 1

        for key, eq in self.model.equation_dict.items():
            scope = self.t_scope.scope_dict[key]
            for eq_method in eq:
                eq_method(scope)
        result = self.t_scope.get_derivatives()
        return [x.get_value() for x in result]