
class ConstraintValidator:
    def validate(self, constraints, plan):

        if not plan:
            return False

        constraints = str(constraints).lower()
        plan = plan.lower()

        if "low" in constraints and ("trek" in plan or "long walk" in plan):
            return False

        if "vegetarian" in constraints and "non-veg" in plan:
            return False

        return True
