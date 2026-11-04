"""The one place the eval touches your bot.

run_eval.py calls ask_bot() once per question and checks what it returns.
"""


def ask_bot(question: str) -> str:
    # Call the function that turns a question into your bot's answer, not Slack
    # itself. Import it at the top of this file and return the answer as text:
    #
    #     from my_bot.main import answer
    #
    #     def ask_bot(question: str) -> str:
    #         return answer(question)
    raise NotImplementedError("Connect your bot in eval/connect.py, then re-run.")
