# main.py
from bot_client import BotClient
from memory_manager import MemoryManager
from knowledge_manager import KnowledgeManager
import json
import re


def sanitize_output(text: str) -> str:
    """将包含 LaTeX/代码块的内容转换为控制台友好的纯文本数学表达。
    规则：
    - 去掉 ``` 代码块围栏
    - 去掉 $$..$$、\(\)、\[\] 包裹；
    - 将 \\frac{a}{b} → (a)/(b)
    - 将 \\Rightarrow/\\to → => / ->
    - 去掉 $...$ 包裹
    - 合并多余空行
    """
    if not isinstance(text, str):
        return str(text)

    # 去代码块围栏 ```...```
    text = re.sub(r"```+\s*([\s\S]*?)```+", r"\1", text)
    # 去 $$...$$
    text = re.sub(r"\$\$\s*([\s\S]*?)\s*\$\$", lambda m: m.group(1).replace("\n", " "), text)
    # 去 \( ... \) 与 \[ ... \]
    text = re.sub(r"\\\(|\\\)", "", text)
    text = re.sub(r"\\\[|\\\]", "", text)
    # \frac{a}{b} -> (a)/(b)
    def _frac_repl(m: re.Match) -> str:
        a = m.group(1).strip()
        b = m.group(2).strip()
        return f"({a})/({b})"
    text = re.sub(r"\\frac\s*\{\s*([^}]*)\s*\}\s*\{\s*([^}]*)\s*\}", _frac_repl, text)
    # 箭头替换
    text = re.sub(r"\\Rightarrow|⇒", "=>", text)
    text = re.sub(r"\\to", "->", text)
    # 去掉 $...$
    text = re.sub(r"\$([^$]+)\$", r"\1", text)
    # 合并 3 个以上空行为 1 个空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 去除行尾多余空格
    text = re.sub(r"[\t ]+\n", "\n", text)
    return text


def main():
    print("🌟 欢迎使用解方程小助手！(◕‿◕✿)")
    print("输入方程题目，我会帮你解答~")
    print("输入 '退出' 或 'quit' 结束对话\n")
    
    # 初始化组件
    bot_client = BotClient()
    memory_manager = MemoryManager()
    knowledge_manager = KnowledgeManager()

    # 缓存当前题目（用于处理“我不会/继续”等跟进输入）
    current_question = None
    
    # 显示当前记忆状态
    print("📚 当前记忆状态：")
    memory_context = memory_manager.get_memory_context()
    print(f"  进步记录：{memory_context['progress'][-1] if memory_context['progress'] else '无'}")
    print(f"  薄弱环节：{memory_context['weak_points'][-1] if memory_context['weak_points'] else '无'}")
    print("-" * 50)
    
    # 跟进输入关键词（表示用户希望继续或需要更细提示）
    followup_keywords = [
        "我不会", "不会", "不懂", "看不懂", "不明白", "再讲一遍", "提示", "继续", "下一步", "help", "再来一次"
    ]

    # 简单判断是否像“方程题目”（用于识别新题而非跟进）
    def looks_like_equation(text: str) -> bool:
        if not text:
            return False
        if "=" in text:
            return True
        if re.search(r"[xyabc]", text, re.IGNORECASE) and re.search(r"[\+\-\*/]", text):
            return True
        return False
    
    while True:
        # 获取用户输入
        user_input = input("📝 请输入方程题目：").strip()
        
        if user_input.lower() in ['退出', 'quit', 'exit']:
            print("👋 再见啦，解题小能手！(•̀ᴗ•́)و")
            break
        
        if not user_input:
            continue

        # 识别是否为“跟进输入”
        is_followup = current_question is not None and any(k in user_input for k in followup_keywords)
        if looks_like_equation(user_input):
            # 明确的新题目
            current_question = user_input
            is_followup = False
        elif current_question is None:
            # 没有历史题目，且不像题目，则把本次作为题目
            current_question = user_input
            is_followup = False
        
        # 获取记忆上下文
        memory_context = memory_manager.get_memory_context()
        
        # 检索外部知识库（阿里云百炼）
        kb_text = knowledge_manager.retrieve_domain_knowledge(current_question or user_input)
        kb_section = ("【知识库内容】\n" + kb_text) if kb_text else "【知识库内容】 暂无"
        
        # 加载多样化词典（颜文字/引导词/情感词），提示模型多样化使用
        lexicon = knowledge_manager.load_lexicon()
        # 为避免过长，这里只挑选前若干项示例注入
        def head(lst, n=5):
            return lst[:n] if isinstance(lst, list) else []
        emoji_demo = {k: head(v, 5) for k, v in lexicon.get('emoji', {}).items()}
        guidance_demo = {k: head(v, 5) for k, v in lexicon.get('guidance', {}).items()}
        emotion_demo = {k: head(v, 5) for k, v in lexicon.get('emotion', {}).items()}
        lexicon_section = (
            "【引导词/情感词/颜文字词典（示例）】\n"
            + json.dumps({
                "emoji": emoji_demo,
                "guidance": guidance_demo,
                "emotion": emotion_demo,
            }, ensure_ascii=False, indent=2)
        )

        # 状态到词典类别映射（要求模型严格按此从词典中取词）
        state_mapping = {
            "blank": {"emoji": "blank", "guidance": "blank", "emotion": "blank"},
            "correct": {"emoji": "correct", "guidance": "correct", "emotion": "correct"},
            "error": {"emoji": "error", "guidance": "error", "emotion": "error", "extra_guidance": "try_again"},
            "partial": {"emoji": "partial", "guidance": "partial", "emotion": "partial", "extra_guidance": "final_push"},
            "almost": {"emoji": "almost", "guidance": "almost", "emotion": "partial", "extra_guidance": "final_push"}
        }
        state_mapping_section = (
            "【状态映射】\n" + json.dumps(state_mapping, ensure_ascii=False, indent=2)
        )
        
        # 构造包含记忆与控制信息的提示（不修改系统提示词，只在用户消息中附加）
        memory_text = f"""
【记忆数据】
- 常见错误库：{', '.join(memory_context['error_patterns']) if memory_context['error_patterns'] else '无记录'}
- 进步记录：{memory_context['progress'][-1] if memory_context['progress'] else '首次使用'}
- 薄弱环节：{memory_context['weak_points'][-1] if memory_context['weak_points'] else '全面均衡'}
- 会话ID：{memory_context['session_id']}

{kb_section}

{lexicon_section}

{state_mapping_section}
""".strip()

        output_control = (
            "【输出控制】\n"
            "- 若为简单过程（仅基础移项/四则运算/1-2步），一次性输出完整解题过程。\n"
            "- 若为中等或复杂过程（括号/分数/3步以上），分步引导并在关键处等待确认，再继续。\n"
            "- 使用与状态匹配且尽量不重复的颜文字/引导词/情感词：\n"
            "  • 正确→自豪/惊喜类；错误→温柔/鼓励类；部分正确→期待/信心类；即将成功→激动/期待类。\n"
            "- 当学生回复‘我不会/不懂/继续/下一步/再讲一遍’等时：务必回到当前同一题目，\n"
            "  提供更小步长的下一步（给出明确算式或操作），不要更换题目，也不要离题拓展。\n"
            "- 词典强制使用规则：每次响应必须从【状态映射】对应类别中至少各选择1项：emoji + guidance + emotion；\n"
            "  对于 error/partial/almost 状态，可额外从 extra_guidance 指定类别再选1项强化鼓励。\n"
            "- 非重复要求：禁止与上一条响应使用完全相同的emoji/guidance/emotion；若无法避免，请替换为同类别的不同备选；\n"
            "  若类别耗尽，可退回到 partial 类别中挑选最接近语义的备选，但需在文本中说明原因。\n"
            "- 输出格式（控制台友好）：使用纯文本数学式，如 (g-1)/(x-1)=1/7；避免使用 $$...$$、\\(\\)、\\[\\]、\\frac、\\Rightarrow 等 LaTeX 语法；\n"
            "  每一步单行表达，可用 1)、2)、3）编号或短句提示；不要输出代码块围栏。\n"
        )

        # 题目与跟进上下文
        effective_question = current_question or user_input
        student_followup = f"学生刚才的回复：{user_input}" if is_followup else ""

        prompt_with_memory = f"""
{memory_text}

{output_control}
题目：{effective_question}
{student_followup}
👉 现在，请用特级教师模式分析并继续：
- 若是跟进输入，请直接从上一步断点继续，给出下一小步与示例；
- 若是新题，按照上述输出控制给出讲解；
- 每次响应包含至少一项【记忆数据】引用。
""".strip()
        
        # 调用智能体
        print("小朋友稍等一下呀！(っ˘▽˘)っ 老师正在思考中呢，马上回答你~~~")
        response = bot_client.call_bot(prompt_with_memory)
        
        if response:
            # 显示回答
            try:
                # 解析 Aliyun/OpenAI 兼容格式
                answer = None
                if isinstance(response, dict):
                    data_content = response.get('data', {}).get('content')
                    if data_content:
                        answer = data_content
                    else:
                        choices = response.get('choices')
                        if isinstance(choices, list) and choices:
                            message = choices[0].get('message') or {}
                            answer = message.get('content')
                if not answer:
                    # 尝试通用字段
                    answer = response.get('output_text') or response.get('message') or str(response)
                # 打印前进行格式清洗
                answer = sanitize_output(answer)
                print(f"\n👩‍🏫 老师的回答：\n{answer}\n")
                
                # 更新记忆（使用原始响应）
                memory_manager.update_memory(response)
                print("💾 记忆已更新！\n")
                
            except Exception as e:
                print(f"解析回答出错：{e}")
                print(f"原始响应：{response}")
        else:
            print("❌ 调用失败，请检查网络和配置\n")

if __name__ == "__main__":
    main()
