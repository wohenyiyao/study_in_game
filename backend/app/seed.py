"""种子数据：管理员账号 + 闯关内容（科目 → 章节 → 关卡 → 题目）。

当前种子：1 个科目「Python 编程」= 2 章 4 关 20 题。
之后新增科目（Java / 面试题库等）可在此追加 SUBJECTS 条目，或在管理后台在线添加。
"""
from .database import Base, engine, SessionLocal, ensure_database
from .models import User, Subject, Chapter, Level, Question
from .auth import hash_password

# subject -> chapters -> levels -> questions
# questions 元组: (content, options, answer_index, explanation)
SUBJECTS = [
    {
        "name": "Python 编程",
        "code": "python",
        "icon": "🐍",
        "description": "从零开始的 Python 闯关之旅：基础语法、流程控制与常用结构",
        "order": 0,
        "chapters": [
            {
                "title": "Python 基础语法",
                "description": "从零认识 Python 的变量、类型与流程控制",
                "levels": [
                    {
                        "title": "变量与数据类型",
                        "description": "掌握变量命名、基本类型与类型转换",
                        "pass_ratio": 0.6,
                        "questions": [
                            ("下列哪个是合法的 Python 变量名？",
                             ["2abc", "_count", "my-var", "class"], 1,
                             "_count 合法：Python 变量可以下划线开头；2abc 不能以数字开头，my-var 含非法连字符，class 是保留字。"),
                            ("type(3.14) 的结果是？",
                             ["int", "float", "str", "decimal"], 1,
                             "3.14 是浮点数，type() 返回其类型 float。"),
                            ("下列哪个是不可变（immutable）数据类型？",
                             ["list", "dict", "tuple", "set"], 2,
                             "tuple（元组）不可变；list/dict/set 都可变。不可变对象可作为字典的键。"),
                            ("执行 '5' + 3 会发生什么？",
                             ["返回 '53'", "返回 8", "抛出 TypeError", "返回 '8'"], 2,
                             "字符串与整数不能直接相加，Python 会抛 TypeError。需先 int('5')+3 或 '5'+str(3)。"),
                            ("a = 10; b = a; a = 20 之后，b 的值是？",
                             ["10", "20", "报错", "None"], 0,
                             "int 是不可变类型，b = a 只是把 b 指向同一个整数 10；之后 a 重新指向 20，b 不受影响。"),
                        ],
                    },
                    {
                        "title": "条件与循环",
                        "description": "if/elif/else 与 for/while 的用法",
                        "pass_ratio": 0.6,
                        "questions": [
                            ("list(range(5)) 的结果是？",
                             ["[1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4]", "[5]", "[0, 5]"], 1,
                             "range(5) 生成 0 到 4（含头不含尾），转成列表即 [0,1,2,3,4]。"),
                            ("x = 0\nwhile x < 5:\n    x += 1\n循环结束后 x 的值是？",
                             ["4", "5", "6", "0"], 1,
                             "x 从 0 加到 5 时条件 x<5 为 False 退出，因此最终 x=5。"),
                            ("下列哪个关键字用于【跳出】当前循环？",
                             ["continue", "pass", "break", "exit"], 2,
                             "break 结束整个循环；continue 跳过本次进入下一次；pass 是空语句占位。"),
                            ("判断整数 x 能否被 3 整除的正确写法是？",
                             ["x / 3 == 0", "x % 3 == 0", "x // 3 == 0", "x ** 3 == 0"], 1,
                             "取模运算符 % 求余数，余数为 0 表示整除；x/3 是除法，结果一般不是 0。"),
                            ("关于 elif，下列说法正确的是？",
                             ["可以没有 if 单独使用", "elif 条件不满足时程序会报错",
                              "用于在前一个条件不满足时继续判断新条件", "elif 后必须跟 else"], 2,
                             "elif = else if，在 if 不成立时继续判断，可多个连用，可省略最后的 else。"),
                        ],
                    },
                ],
            },
            {
                "title": "函数与常用结构",
                "description": "函数、作用域，以及列表/字典这些高频结构",
                "levels": [
                    {
                        "title": "函数与作用域",
                        "description": "参数、返回值、全局与局部变量",
                        "pass_ratio": 0.6,
                        "questions": [
                            ("def f(a, b=2): return a * b\nf(3) 的返回值是？",
                             ["5", "6", "报错", "None"], 1,
                             "b 有默认值 2，调用 f(3) 时只传 a=3，返回 3*2=6。"),
                            ("函数体内没有 return 语句时，返回值是？",
                             ["0", "False", "None", "抛异常"], 2,
                             "没有 return（或裸 return）的函数默认返回 None。"),
                            ("在函数内部给全局变量赋值，正确做法是？",
                             ["直接赋值即可", "global x", "nonlocal x", "static x"], 1,
                             "函数内对全局变量赋值需要用 global 声明；nonlocal 用于嵌套函数的外层变量。"),
                            ("def f(*args): ...，调用 f(1, 2, 3) 时 args 是？",
                             ["一个列表", "一个元组", "一个整数 3", "报错"], 1,
                             "*args 把所有位置参数打包成元组 (1, 2, 3)。"),
                            ("函数参数按默认传参方式属于哪种传递？",
                             ["引用传递", "值传递", "传对象引用（共享对象，不可变类型表现为值传递）",
                              "指针传递"], 2,
                             "Python 是传对象引用：可变对象会被修改到原对象，不可变对象（int/str）改的是新引用。"),
                        ],
                    },
                    {
                        "title": "列表与字典",
                        "description": "切片、推导式、字典方法与集合去重",
                        "pass_ratio": 0.6,
                        "questions": [
                            ("lst = [10, 20, 30, 40, 50]\nlst[1:3] 的结果是？",
                             ["[10, 20]", "[20, 30]", "[20, 30, 40]", "[30, 40]"], 1,
                             "切片含头不含尾：下标 1 到 2，即 [20, 30]。"),
                            ("lst.append(x) 与 lst.extend([x]) 的区别是？",
                             ["没有区别", "append 加单个元素，extend 拼接序列元素",
                              "append 只能加数字", "extend 会覆盖原列表"], 1,
                             "append 把 x 作为一个元素加入；extend 把可迭代对象里的每个元素分别加入。"),
                            ("d = {'a': 1}\nd.get('b', 99) 的返回值是？",
                             ["报 KeyError", "None", "99", "False"], 2,
                             "dict.get(key, default) 键不存在时返回默认值 99，不抛异常。"),
                            ("对列表 [1, 2, 2, 3, 3, 3] 去重最简洁的方式是？",
                             ["set([1,2,2,3,3,3])", "遍历+判断", "sort()", "reverse()"], 0,
                             "set() 集合天然去重，list(set(...)) 可得到去重后的列表。"),
                            ("[x * x for x in range(4)] 的结果是？",
                             ["[0, 1, 4, 9]", "[1, 4, 9]", "[0, 1, 2, 3]", "[4, 4, 4, 4]"], 0,
                             "列表推导式对 range(4) 即 0,1,2,3 求平方，得到 [0, 1, 4, 9]。"),
                        ],
                    },
                ],
            },
        ],
    },
]


def seed() -> None:
    ensure_database()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == "admin").first() is None:
            db.add(User(email="admin@learn-quest.local",
                        password_hash=hash_password("admin123"), role="admin"))
        if db.query(Subject).first() is not None:
            print("已存在内容，跳过种子题目（如需重置请重建数据库后重跑）")
            return
        for s_i, s_data in enumerate(SUBJECTS):
            sub = Subject(name=s_data["name"], code=s_data["code"],
                          icon=s_data.get("icon", "🎮"),
                          description=s_data.get("description", ""),
                          order=s_data.get("order", s_i))
            db.add(sub)
            db.flush()
            for c_i, ch_data in enumerate(s_data["chapters"]):
                ch = Chapter(subject_id=sub.id, title=ch_data["title"],
                             description=ch_data.get("description", ""), order=c_i)
                db.add(ch)
                db.flush()
                for lv_i, lv_data in enumerate(ch_data["levels"]):
                    lv = Level(chapter_id=ch.id, title=lv_data["title"],
                               description=lv_data.get("description", ""),
                               order=lv_i, pass_ratio=lv_data.get("pass_ratio", 0.6))
                    db.add(lv)
                    db.flush()
                    for q_i, (content, options, ans, exp) in enumerate(lv_data["questions"]):
                        db.add(Question(level_id=lv.id, content=content,
                                        options=list(options), answer_index=ans,
                                        explanation=exp, order=q_i))
        db.commit()
        n_sub = db.query(Subject).count()
        n_lv = db.query(Level).count()
        n_q = db.query(Question).count()
        print(f"种子数据完成：{n_sub} 个科目，{n_lv} 个关卡，{n_q} 道题 + 管理员(admin/admin123)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
