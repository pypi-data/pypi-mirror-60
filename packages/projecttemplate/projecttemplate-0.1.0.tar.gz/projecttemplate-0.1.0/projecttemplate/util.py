from typing import Any, Hashable, KeysView


class AttrDict(dict):
    def __getattr__(self, attr: Hashable) -> Any:
        return self[attr]

    def __setattr__(self, attr: Hashable, value: Any) -> None:
        self[attr] = value

    def __dir__(self) -> KeysView:
        return self.keys()

    def _ipython_key_completions_(self) -> KeysView:
        return self.keys()

    def __repr__(self) -> str:
        repr_ = [
            "Name             | Type        | Shape       ",
            "-----------------+-------------+-------------",
        ]
        for key, value in self.items():
            repr_.append(
                "{v:16} | {t:11} | {s!s:8}".format(
                    v=key,
                    t=type(value).__name__,
                    s=value.shape if hasattr(value, "shape") else "",
                )
            )
        return "\n".join(repr_)
