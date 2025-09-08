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
            name (str): name of the problem.

            problem_type (str): The type of problem. "Termination", "Search", "Function

            state_variables (List[str]): Names of variables

            initialization_rules (List[str]): Rules to set up the initial state from 'input'

            transition_rules (List[Tuple[str, str]]): The core logic as (condition, action) pairs.
                                                      Example: [("n % 2 == 0", "n = n // 2")].

            termination_condition (str): The condition for halting (e.g., "n == 1").
        """
        self.name = name
        self.problem_type = problem_type
        self.state_variables = state_variables
        self.initialization_rules = initialization_rules
        self.transition_rules = transition_rules
        self.termination_condition = termination_condition

    def __repr__(self) -> str:
        """Provides a concise representation of the NTS object."""
        return f"<NTS name='{self.name}' type='{self.problem_type}' vars={self.state_variables}>"

    def simulate(self, input_value: int, max_steps: int = 1000) -> Dict[str, Any]:
        """
        Simulates the execution of the NTS for a given input.

        Args:
            input_value (int): The starting integer for the simulation.
            max_steps (int):

        Returns:
            A dictionary containing the results of the simulation.
        """
        # The 'state' dictionary will hold the current values of our state variables.
        # It also serves as the local namespace for exec() and eval().
        # NOTE: Using exec/eval is safe here because we control the rule strings.

        # 1. Initialization
        local_scope = {'input': input_value}
        for rule in self.initialization_rules:
            exec(rule, {}, local_scope)

        # Extract only the defined state variables into our main state dict
        state = {var: local_scope[var] for var in self.state_variables}

        history = [state.copy()]
        terminated = False
        steps = 0

        # 2. Simulation Loop
        for i in range(max_steps):
            steps = i
            # Create a copy of the state for this step's evaluation
            current_scope = state.copy()

            # Check for termination first
            if eval(self.termination_condition, {}, current_scope):
                terminated = True
                break

            # Apply the first transition rule whose condition is met
            rule_applied = False
            for condition, action in self.transition_rules:
                if eval(condition, {}, current_scope):
                    exec(action, {}, current_scope)
                    # Update the main state from the modified scope
                    state = {var: current_scope[var] for var in self.state_variables}
                    history.append(state.copy())
                    rule_applied = True
                    break  # Ensure only one rule fires per step

            if not rule_applied:
                return {
                    'terminated': False, 'reason': 'Stuck (no rule applied)',
                    'steps': steps, 'final_state': state, 'history': history
                }

        # 3. Format and return result
        reason = "Terminated" if terminated else "Max steps reached"
        return {
            'terminated': terminated, 'reason': reason, 'steps': steps,
            'final_state': state, 'history': history
        }


# --- Example Usage, collatz conjecture ---
# if __name__ == "__main__":
#     # Define the Weak Collatz Conjecture as an NTS
#     collatz_nts = NumberTheoreticSystem(
#         name="Weak Collatz Conjecture",
#         problem_type="Search",
#         state_variables=['n'],
#         initialization_rules=["n = input"],
#         transition_rules=[
#             ("n % 2 == 0", "n = n // 2"),
#             ("n % 2 != 0", "n = 3*n + 1")
#         ],
#         termination_condition="n == 1"
#     )
#
#     print(f"Created NTS: {collatz_nts}")
#     print("-" * 30)
#
#     # Simulate the NTS with a starting input of 10
#     start_input = 10
#     print(f"Simulating for input = {start_input}...")
#     result = collatz_nts.simulate(start_input)
#
#     # Print the results
#     print(f"Terminated: {result['terminated']} ({result['reason']})")
#     print(f"Steps: {result['steps']}")
#     print(f"Final State: {result['final_state']}")
#     print("History:")
#     for i, state in enumerate(result['history']):
#         print(f"  Step {i}: {state}")
