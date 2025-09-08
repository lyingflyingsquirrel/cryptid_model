from typing import List, Tuple, Dict, Any


class NumberTheoreticSystem:
    """
    A structured representation of a number theory problem defined by rules
    operating on a set of state variables.
    """

    def __init__(
            self,
            name: str,
            problem_type: str,
            state_variables: List[str],
            initialization_rules: List[str],
            transition_rules: List[Tuple[str, str]],
            termination_condition: str,
    ):
        """
        Initializes the Number Theoretic System.
        Args:
            name (str): Human-readable name (e.g., "Weak Collatz Conjecture").
            problem_type (str): The type of problem (e.g., "Termination", "Search").
            state_variables (List[str]): Names of variables the system uses (e.g., ['n']).
            initialization_rules (List[str]): Rules to set up the initial state from 'input'
                                              (e.g., ["n = input"]).
            transition_rules (List[Tuple[str, str]]): The core logic as (condition, action) pairs.
                                                      Example: [("n % 2 == 0", "n = n // 2")].
            termination_condition (str): The condition for halting (e.g., "n == 1").
        """
        self.name = name
        self.problem_type = problem_type
        self.state_variables = state_variables
        self.initialization_rules = initialization_rules
        # Replace Python's integer division // with / for Laconic
        self.transition_rules = [(c, a.replace('//', '/')) for c, a in transition_rules]
        self.termination_condition = termination_condition

    def __repr__(self) -> str:
        """Provides a concise representation of the NTS object."""
        return f"<NTS name='{self.name}' type='{self.problem_type}' vars={self.state_variables}>"

    def to_laconic(self) -> str:
        """
        Translates the NTS rules into a string of Laconic code.
        """
        if self.problem_type != "Termination":
            raise NotImplementedError(
                f"Laconic compilation for problem type '{self.problem_type}' is not yet supported.")

        # 1. Variable declarations
        var_declarations = "\n".join([f"var {var};" for var in self.state_variables])

        # 2. Initialization
        initialization_code = "\n".join([f"{rule};" for rule in self.initialization_rules])

        # 3. Main loop and conditions
        # The while loop runs as long as the termination condition is NOT met.
        loop_condition = self.termination_condition.replace("==", "!=")

        # Build the if/else if/else chain
        if_chain = ""
        for i, (condition, action) in enumerate(self.transition_rules):
            action_code = f"  {action.strip()};"
            if i == 0:
                if_chain += f"  if ({condition}) {{\n    {action_code}\n  }}"
            else:
                # For simplicity, we'll assume the second condition is the 'else' block
                if_chain += f" else {{\n    {action_code}\n  }}"

        # Assemble the final code using a template
        laconic_code = f"""
{var_declarations}
{initialization_code}

while ({loop_condition}) {{
{if_chain}
}}
"""
        return laconic_code.strip()

    def simulate(self, input_value: int, max_steps: int = 1000) -> Dict[str, Any]:
        """
        Simulates the execution of the NTS for a given input.
        """
        local_scope = {'input': input_value}
        for rule in self.initialization_rules:
            exec(rule, {}, local_scope)

        state = {var: local_scope[var] for var in self.state_variables}
        history = [state.copy()]
        terminated = False
        steps = 0

        for i in range(max_steps):
            steps = i
            current_scope = state.copy()

            if eval(self.termination_condition, {}, current_scope):
                terminated = True
                break

            rule_applied = False
            for condition, action in self.transition_rules:
                # We use the original Python-compatible rules for simulation
                py_action = action.replace('/', '//')
                if eval(condition, {}, current_scope):
                    exec(py_action, {}, current_scope)
                    state = {var: current_scope[var] for var in self.state_variables}
                    history.append(state.copy())
                    rule_applied = True
                    break

            if not rule_applied:
                return {
                    'terminated': False, 'reason': 'Stuck (no rule applied)',
                    'steps': steps, 'final_state': state, 'history': history
                }

        reason = "Terminated" if terminated else "Max steps reached"
        return {
            'terminated': terminated, 'reason': reason, 'steps': steps,
            'final_state': state, 'history': history
        }

