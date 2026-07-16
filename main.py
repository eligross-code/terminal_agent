from agent_infra.backend.agents import AgentRuntime, Model


def main():
    model = Model(level="local")
    runtime = AgentRuntime(model=model, max_steps=10)

    print("NOVA terminal runtime. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_message:
            continue

        if user_message.lower() in {"exit", "quit"}:
            break

        response, _tps_time_series = runtime.loop(user_message)
        print(f"NOVA: {response}")
        print(("Average tokens per second over time per generation: " + ", ".join(f"{tps:.2f}" for tps in _tps_time_series)))


if __name__ == "__main__":
    main()
