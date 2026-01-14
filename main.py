from agents.manager_agent import ManagerAgent

def main():
    print("\n====== TRAVELMIND AGENTIC AI SYSTEM ======\n")

    user_input = input("Describe your travel needs: ")
    destination = input("Destination: ")
    days = int(input("Number of days: "))

    manager = ManagerAgent()
    result = manager.build_travel_plan(user_input, destination, days)

    print("\n========== USER CONSTRAINTS ==========\n")
    print(result["constraints"])

    print("\n========== PLAN SCORES ==========\n")
    for k, v in result["scores"].items():
        print(f"{k.capitalize()} Agent Score: {v}")

    print("\n========== FINAL OPTIMIZED PLAN ==========\n")
    print(result["final_plan"])

if __name__ == "__main__":
    main()

