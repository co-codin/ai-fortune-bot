# AI Fortune Bot (@AIFortuneBaziBot)

Telegram bot for Chinese and Western divination, written in Python
(python-telegram-bot). Real calculations (lunar-python for BaZi, PyEphem for
planetary positions) with LLM-written interpretations (any OpenAI-compatible API).

## Features
- **BaZi (八字)** four pillars, Five Elements balance, saved birth data
- **Tarot** — 78-card Rider–Waite–Smith deck with card images
- **Astrology** — sun/moon/rising-aware horoscope, compatibility (合盘)
- **Dream interpretation, temple lots (24 original 签), I Ching, daily luck, almanac (黄历)**
- Languages: 中文 / English / Русский (`/lang`), timezone `/tz`, `/daily`
- Share/referral links, per-user rate limit, `/stats` for admins
- Telegram Stars premium stub, **disabled** by default (`PAYMENTS_ENABLED=false`)

## Setup & running
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in values, never commit .env
set -a; . ./.env; set +a
./run.sh               # foreground
./run-nohup.sh         # background (setsid), logs to bot.log, pid in bot.pid
```
systemd unit: `deploy/fortune-bot.service`.

## Environment variables
See `.env.example`. Required: `FORTUNE_BOT_TOKEN`. LLM (optional):
`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`. Optional: `LLM_TIMEOUT`,
`BOT_USERNAME`, `FORTUNE_DB`, `ADMIN_IDS`, `RATE_LIMIT_PER_MIN`, `PAYMENTS_ENABLED`, `PREMIUM_STARS`.

## Tests
```bash
.venv/bin/python -m pytest -q    # 183 tests
```

## Licensing
- Tarot images in `assets/cards/` are the 1909 Rider–Waite–Smith deck
  (art by Pamela Colman Smith), in the public domain.
- No license file is included for the code yet; all rights reserved by the author.

---

## 中文说明

只供娱乐。界面支持中文、Русский 和 English：用 `/lang` 切换，或按 Telegram 的 language_code 自动识别。

## 功能
| 模式 | 内容 |
|---|---|
| 🀄 八字 `/bazi` | 依次输入日期、时间、城市或时区，排出四柱（用 lunar-python 计算）和五行分布，并给出 AI 或模板解读。另有"详细流年运势"付费按钮 |
| 📜 黄历 `/huangli` | 今日农历、日柱、宜、忌 |
| 🃏 塔罗 `/tarot` | 完整 78 张牌，正位和逆位各有含义，用系统随机源（CSPRNG）抽牌。有每日一张和过去/现在/未来三张两种牌阵，三张牌阵可以先写下问题 |
| ♈ 星座 `/astro` | 太阳和月亮星座用 PyEphem 计算。上升星座需要出生时间和城市坐标，目前只内置了少数城市的坐标。附每日运势 |
| 💞 合盘 `/compat` | 输入两人的出生日期，得出五行契合度、星座元素契合度和总结 |
| ☀️ 每日推送 `/daily on [0-23]`、`/daily off` | 在你所在时区的指定整点推送：今日日柱、今日塔罗和星座运势 |
| 📤 分享 | 生成分享文字和链接 `t.me/<bot>?start=ref_<uid>`，推荐关系记录在 SQLite |
| 💫 付费 | 用 Telegram Stars（XTR）开 sendInvoice，默认关闭（`PAYMENTS_ENABLED=false`），关闭时只提示"即将上线" |
| 🌙 解梦 `/dream` | 用户描述梦境后由 AI 解读，结合周公解梦和心理学，不做预言。没有 AI 时，用内置的 14 类常见意象词典（三种语言）解读 |
| 🎋 求签 `/lot` | 24 支**原创**签：签等加七言签诗加签解，用系统随机源抽签。这些签不是观音灵签或其他寺庙签谱，界面上也写明了 |
| ☯️ 易经 `/iching` | 三枚铜钱摇六次，每爻 6、7、8、9 的概率分别是 1/8、3/8、3/8、1/8。给出本卦、变爻和之卦，覆盖全部 64 卦（文王卦序，中英俄卦名），再由 AI 解读 |
| 🍀 今日幸运 `/lucky` | 根据日主和今日日柱的五行（取生扶日主的五行）推出幸运色、幸运数字（河图数）和方位；每日推送里也会附上 |
| 🛡 | 每个用户都有限频；管理员可用 `/stats` 查看用户数、推荐人数和各模式使用次数 |

## 交互
- 第一次打开会先选语言，默认选中 Telegram 客户端的语言。
- 日期依次选年代、年、月、日（也可以直接输入）；时辰有 12 个按钮外加"不知道"；城市可以点 8 个常用城市，也可以自己输入。
- 用户的出生资料会保存下来，下次可以选"用保存的资料"。
- 菜单直接在原消息上更新；每个结果后面都有"再来一次 / 换个牌阵""分享""主菜单"按钮。
- 回复超过 0.4 秒时显示"正在输入…"。消息用 HTML 格式，LLM 返回的 Markdown 会先转义再转换。
- 塔罗牌配有 1909 年 Rider–Waite–Smith 原版牌面图（Pamela Colman Smith 绘，公有领域，取自 Wikimedia Commons），保存在 `assets/cards/`，逆位牌会把图片倒过来。
- 每种语言都设置了命令菜单（setMyCommands）、bot 简介（setMyDescription）和短简介（setMyShortDescription）。
- 时辰按钮按一个代表时间来算，比如子时按 00:00、丑时按 02:00。所以选"子时"相当于早子时，晚子时（23 点以后）请直接输入准确时间。

## 计算说明
- **年柱、月柱**：按节气的确切时刻来定。lunar-python 里节气时间用的是东八区，所以先把出生时间换算成 UTC+8 再算。**日柱、时柱**：用出生地当地的钟表时间。**子时**：沿用 lunar-python 的 sect 2，23 点以后日柱不变，时干按次日推。没有做真太阳时修正。
- 合盘只用出生日期，所以只取年、月、日三柱，统一按中午、东八区计算；星座按日期表判断，在交界那一天可能差一天。
- 小阿卡纳的牌义是用"花色领域 + 点数关键词"组合出来的，这是常见的教学写法；大阿卡纳每张牌都单独写了牌义。

## 运行
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q                       # 158 项测试
FORTUNE_BOT_TOKEN=xxx ./run.sh            # 前台运行
FORTUNE_BOT_TOKEN=xxx ./run-nohup.sh      # 后台运行，日志写到 bot.log，停止：kill $(cat bot.pid)
# 或者用 systemd --user，见 deploy/fortune-bot.service
```

## 环境变量
| 变量 | 是否必填 | 说明 |
|---|---|---|
| `FORTUNE_BOT_TOKEN` | ✅ | BotFather token，只从环境变量读取，不会写进任何文件 |
| `LLM_BASE_URL` `LLM_API_KEY` `LLM_MODEL` | 可选 | 兼容 OpenAI 的接口，例如 `https://api.openai.com/v1`。三个必须都设置；没设或者调用失败时，自动改用模板解读 |
| `LLM_TIMEOUT` | 可选 | 默认 45 秒 |
| `FORTUNE_DB` | 可选 | SQLite 路径，默认 `fortune.db` |
| `BOT_USERNAME` | 可选 | 分享链接里用的 bot 用户名；不设就在启动时通过 getMe 获取 |
| `ADMIN_IDS` | 可选 | 可以使用 `/stats` 的 Telegram 用户 ID，多个用逗号分隔 |
| `PAYMENTS_ENABLED` | 可选 | 默认 `false`；设为 `true` 才会真正发出 Stars 账单 |
| `PREMIUM_STARS` | 可选 | 价格，单位是 Stars，默认 100 |
| `RATE_LIMIT_PER_MIN` | 可选 | 每个用户每分钟最多算几次，默认 6 |

## 结构
```
fortune_bot/bazi.py     八字、节气、黄历、五行合盘
fortune_bot/tarot.py    78 张牌，三语牌义，CSPRNG 抽牌
fortune_bot/astro.py    太阳、月亮、上升星座，星座配对
fortune_bot/llm.py      可选的 OpenAI 兼容接口，失败时返回 None
fortune_bot/i18n.py     中、俄、英三语文本和模板
fortune_bot/engine.py   与 Telegram 无关的对话逻辑，便于测试
fortune_bot/storage.py  SQLite：users、readings、payments
fortune_bot/app.py      python-telegram-bot 适配层和每日推送任务
tests/                  八字、塔罗、星座、i18n、对话流程（mock 掉 Telegram Bot）
```

## AI 设置
- 推荐模型：`gpt-4o`。我用同一个塔罗问题实测对比过：gpt-4o-mini 不遵守"不要 Markdown"的要求，还会给出"辞职吧"这类指令式建议；gpt-4o 写出来的是纯文本，语气克制，俄语也更自然。
- 每种模式都有单独的系统提示词（见 `fortune_bot/prompts.py`），统一规定：纯文本、限定字数、只供娱乐、不给医疗、法律或财务建议、不替用户做决定、不预言死亡或疾病；遇到自伤等危机内容时，建议用户求助，不做占卜；用户输入中的"指令"一律忽略。

## 安全
- 所有输出都先做 HTML 转义，再转换 `**`、`*`、反引号这三种标记（有模糊测试覆盖）。
- 回调数据可能被篡改，所以全部做了校验，格式不对就忽略。
- 输入有长度上限：问题 300 字、梦 1500 字、日期、时间和城市各 100 字。
- 每个用户都有限频。
- SQLite 开启了 WAL 和 busy_timeout，可写的列名有白名单。
- 超长消息会自动分段发送；出错时统一给用户回复一条提示。
