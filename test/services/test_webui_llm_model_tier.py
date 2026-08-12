import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import config
from app.models.llm_provider import get_llm_provider

ROOT_DIR = Path(__file__).parent.parent.parent
WEBUI_MAIN = ROOT_DIR / "webui" / "Main.py"


def _widget_by_key(elements, key_prefix):
    return next(
        item
        for item in elements
        if str(getattr(item, "key", "")) == key_prefix
        or str(getattr(item, "key", "")).startswith(f"{key_prefix}_")
    )


class TestGeminiModelTierPicker(unittest.TestCase):
    """
    Gemini 的 Pro 档位是付费模型，很多用户只有免费额度。这里验证 WebUI
    新增的"模型档位"快速选择器：默认落在 Registry 的 Pro 默认值上（不改变
    历史行为），切换到 Flash / Flash-Lite 会直接写入免费额度更友好的模型名，
    选择 Custom 才回退到自由输入框。

    每个用例都用独立的 config.app 字典和 patch 过的 save_config，既避免
    真的写到仓库里的 config.toml，也避免用例之间通过共享的全局 config.app
    / Streamlit session state 互相污染（AppTest 的 session state 在同一
    进程内的多次实例化之间不是完全隔离的）。
    """

    def _open_gemini_panel(self, test_config):
        app = AppTest.from_file(str(WEBUI_MAIN), default_timeout=30)
        app.session_state["ui_language"] = "en"
        # LLM Provider 选择器在设置弹窗（st.dialog）里，需要先打开弹窗才能
        # 在 AppTest 的元素树里找到里面的控件。
        app.session_state["settings_dialog_open"] = True
        app.run()
        provider_select = _widget_by_key(app.selectbox, "llm_provider_select")
        provider_select.set_value("gemini").run()
        self.assertEqual([str(item.value) for item in app.exception], [])
        return app

    def test_defaults_to_pro_tier_matching_registry_default(self):
        test_config = {}
        with (
            patch.object(config, "app", test_config),
            patch.object(config, "save_config"),
        ):
            app = self._open_gemini_panel(test_config)
            tier_select = _widget_by_key(app.selectbox, "gemini_model_tier_select")
            self.assertEqual(tier_select.value, "Gemini Pro (paid, most capable)")
            # 未覆盖时配置里存的是空字符串（表示"跟随 Registry 默认值"），
            # 实际生效的模型名要通过 resolve_model_name 解析。
            resolved_model = get_llm_provider("gemini").resolve_model_name(
                test_config.get("gemini_model_name")
            )
            self.assertEqual(resolved_model, "gemini-3.1-pro-preview")

    def test_switching_to_flash_tier_writes_free_tier_friendly_model(self):
        test_config = {}
        with (
            patch.object(config, "app", test_config),
            patch.object(config, "save_config"),
        ):
            app = self._open_gemini_panel(test_config)
            tier_select = _widget_by_key(app.selectbox, "gemini_model_tier_select")
            tier_select.set_value("Gemini Flash (fast, generous free tier)").run()

            self.assertEqual(
                test_config.get("gemini_model_name"), "gemini-3.1-flash-preview"
            )
            self.assertEqual([str(item.value) for item in app.exception], [])

    def test_switching_to_flash_lite_tier_writes_free_tier_friendly_model(self):
        test_config = {}
        with (
            patch.object(config, "app", test_config),
            patch.object(config, "save_config"),
        ):
            app = self._open_gemini_panel(test_config)
            tier_select = _widget_by_key(app.selectbox, "gemini_model_tier_select")
            tier_select.set_value(
                "Gemini Flash-Lite (fastest, most free-tier friendly)"
            ).run()

            self.assertEqual(
                test_config.get("gemini_model_name"), "gemini-3.1-flash-lite-preview"
            )

    def test_custom_tier_reveals_free_text_model_name_input(self):
        test_config = {}
        with (
            patch.object(config, "app", test_config),
            patch.object(config, "save_config"),
        ):
            app = self._open_gemini_panel(test_config)
            tier_select = _widget_by_key(app.selectbox, "gemini_model_tier_select")
            tier_select.set_value("Custom").run()

            model_name_input = _widget_by_key(
                app.text_input, "gemini_model_name_input"
            )
            model_name_input.set_value("gemini-experimental-1206").run()

            self.assertEqual(
                test_config.get("gemini_model_name"), "gemini-experimental-1206"
            )
            self.assertEqual([str(item.value) for item in app.exception], [])


if __name__ == "__main__":
    unittest.main()
