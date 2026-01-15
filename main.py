from agents.manager_agent import ManagerAgent

def main():
    print("\n====== TRAVELMIND PERSONAL AI ======\n")

    username = input("Enter your name: ")
    user_input = input("Describe your travel needs: ")
    destination = input("Destination: ")
    days = int(input("Number of days: "))

    manager = ManagerAgent()
    result = manager.build_travel_plan(username, user_input, destination, days)

    print("\n========== PERSONALIZED CONSTRAINTS ==========\n")
    print(result["constraints"])

    print("\n========== PERSONALIZED FINAL PLAN ==========\n")
    print(result["final_plan"])

if __name__ == "__main__":
    main()

