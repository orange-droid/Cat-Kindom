def can_capture(attacker, defender):
    """判断是否可以捕获棋子"""
    # 示例捕获规则：骑士可以捕获农民
    capture_rules = {
        "骑士": ["农民","卫兵","弓箭手","骑士"],
        "卫兵": ["农民","卫兵"],
        "弓箭手": ["农民","卫兵","弓箭手"],
        "国王": ["农民","卫兵","弓箭手","骑士","国王"],
        "农民": ["国王","农民"]
    }
    return defender in capture_rules.get(attacker, [])