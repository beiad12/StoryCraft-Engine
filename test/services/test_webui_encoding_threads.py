import os
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

ROOT_DIR = Path(__file__).parent.parent.parent
WEBUI_MAIN = ROOT_DIR / "webui" / "Main.py"


def _widget_by_key(elements, key_prefix):
    return next(
        item
        for item in elements
        if str(getattr(item, "key", "")) == key_prefix
        or str(getattr(item, "key", "")).startswith(f"{key_prefix}_")
    )


class TestEncodingThreadsControl(unittest.TestCase):
    """
    请求模型的 n_threads 默认值是保守的 2（避免服务端并发多任务时抢
    CPU），但 WebUI 之前完全没有入口调整它，所有 WebUI 用户不管机器有多少
    核心都被锁在 2 个编码线程上。这里验证 WebUI 新增的滑块存在，且默认值
    会跟随当前机器的 CPU 核心数（而不是固定的 2），并且可以被用户手动调低。
    """

    def test_defaults_above_two_on_multi_core_machine_and_is_adjustable(self):
        app = AppTest.from_file(str(WEBUI_MAIN), default_timeout=30)
        app.session_state["ui_language"] = "en"
        app.run()
        self.assertEqual([str(item.value) for item in app.exception], [])

        threads_slider = _widget_by_key(app.slider, "n_threads_slider")

        cpu_count = os.cpu_count() or 2
        expected_default = min(8, max(2, cpu_count))
        self.assertEqual(threads_slider.value, expected_default)

        threads_slider.set_value(1).run()
        self.assertEqual([str(item.value) for item in app.exception], [])
        threads_slider = _widget_by_key(app.slider, "n_threads_slider")
        self.assertEqual(threads_slider.value, 1)


if __name__ == "__main__":
    unittest.main()
