"""EN-only server and Android package definitions."""

server = "en"

EN_PACKAGE = "com.YoStarEN.AzurLane"
VALID_SERVER = ["en"]
VALID_PACKAGE = {EN_PACKAGE: "en"}
VALID_CHANNEL_PACKAGE = {}

# Known Azur Lane clients deliberately rejected by this fork. The mapping is
# retained only to provide a precise migration/startup error; these packages
# are never accepted as runtime targets.
UNSUPPORTED_PACKAGE = {
    "com.bilibili.azurlane": "CN",
    "com.YoStarJP.AzurLane": "JP",
    "com.hkmanjuu.azurlane.gp": "TW",
    "com.bilibili.blhx.huawei": "CN channel",
    "com.bilibili.blhx.honor": "CN channel",
    "com.bilibili.blhx.mi": "CN channel",
    "com.tencent.tmgp.bilibili.blhx": "CN channel",
    "com.bilibili.blhx.baidu": "CN channel",
    "com.bilibili.blhx.qihoo": "CN channel",
    "com.bilibili.blhx.nearme.gamecenter": "CN channel",
    "com.bilibili.blhx.vivo": "CN channel",
    "com.bilibili.blhx.mz": "CN channel",
    "com.bilibili.blhx.dl": "CN channel",
    "com.bilibili.blhx.lenovo": "CN channel",
    "com.bilibili.blhx.uc": "CN channel",
    "com.bilibili.blhx.mzw": "CN channel",
    "com.yiwu.blhx.yx15": "CN channel",
    "com.bilibili.blhx.m4399": "CN channel",
    "com.bilibili.blhx.bilibiliMove": "CN channel",
    "com.hkmanjuu.azurlane.gp.mc": "TW channel",
}

DICT_PACKAGE_TO_ACTIVITY = {
    EN_PACKAGE: "com.manjuu.azurlane.PrePermissionActivity",
}

VALID_SERVER_LIST = {
    "en": ["Avrora", "Lexington", "Sandy", "Washington", "Amagi", "Little Enterprise"],
}


def set_server(package_or_server: str):
    """Set the global server; only EN is accepted."""
    global server
    server = to_server(package_or_server)

    from module.base.resource import release_resources
    release_resources()


def to_server(package_or_server: str) -> str:
    """Convert an EN package/server value to ``en``.

    ``auto`` is treated as EN for config migration; actual package detection
    still verifies that the installed package is the EN client.
    """
    if package_or_server in ("auto", "en", EN_PACKAGE):
        return "en"
    if package_or_server in UNSUPPORTED_PACKAGE:
        raise ValueError(f"Unsupported client: EN-only fork: {package_or_server}")
    raise ValueError(f"Unsupported client/server: EN-only fork: {package_or_server}")


def to_package(package_or_server: str) -> str:
    """Convert ``auto``/``en``/the EN package to the EN package name."""
    if package_or_server in ("auto", "en", EN_PACKAGE):
        return EN_PACKAGE
    if package_or_server in UNSUPPORTED_PACKAGE:
        raise ValueError(f"Unsupported client: EN-only fork: {package_or_server}")
    raise ValueError(f"Unsupported client/server: EN-only fork: {package_or_server}")
