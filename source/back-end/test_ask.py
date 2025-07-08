import requests

def main():
    question = input("Enter your question: ").strip()
    if not question:
        print("No question provided, exiting.")
        return

    k_input = input("Number of passages to retrieve (k) [default 3]: ").strip()
    try:
        k = int(k_input) if k_input else 3
    except ValueError:
        print(f"Invalid number '{k_input}', using default k=3.")
        k = 3

    resp = requests.post(
        "http://localhost:8080/ask",
        json={"question": question, "k": k}
    )
    print(f"\nStatus code: {resp.status_code}\n")

    if resp.ok:
        data = resp.json()
        print("=== Answer ===\n")
        print(data.get("answer", "No answer returned."), "\n")
        print("=== Sources ===")
        for idx, src in enumerate(data.get("sources", []), 1):
            print(f"{idx}. {src}")
    else:
        print("Error calling API:", resp.text)

if __name__ == "__main__":
    main()
