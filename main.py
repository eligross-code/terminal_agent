from agent_infra.backend.agents import AgentRuntime, Model


def main():
    model = Model(level="local")
    runtime = AgentRuntime(model=model, max_steps=10)

    print("NOVA terminal runtime. Type 'exit' or 'quit' to stop.")

    ### print stats

    print(f"Total tokens used: {runtime.get_total()}")

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

        avg_tps = sum(_tps_time_series) / len(_tps_time_series) if _tps_time_series else 0.0
        print(("Average tokens per second over time per generation: {avg_tps:.2f} tps"))


if __name__ == "__main__":
    main()
