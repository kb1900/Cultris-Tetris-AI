from c2ai import build_absolute_path
from sys import argv

last_argument = argv[-1]

if not last_argument.endswith(".py"):
    target = ["c2ai", "learning", last_argument, "tetris"]
    _pkg = __import__(".".join(target), globals(), locals(), ["main"])
else:
    _pkg = __import__(
        "c2ai.learning.deap.pso.downstack.tetris", globals(), locals(), ["main"]
    )

_pkg.main()
