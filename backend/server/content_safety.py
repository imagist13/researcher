"""
内容安全检查工具
Content safety checking utilities
"""
import re
from typing import List, Tuple, Dict


class ContentSafetyChecker:
    """内容安全检查器，帮助用户避免API内容风险"""
    
    # 敏感关键词列表（优化后的智能检测）
    RISKY_KEYWORDS = {
        'politics': [
            '政治敏感', '政府内幕', '选举舞弊', '政党斗争', '官员腐败', 
            '示威游行', '政治革命', '敏感政策', '政治制裁', '政治冲突'
        ],
        'violence': [
            '暴力事件', '武装冲突', '军事机密', '恐怖袭击', 
            '血腥暴力', '死亡威胁', '暴力犯罪', '武器制造'
        ],
        'religion': [
            '宗教冲突', '宗教极端', '宗教歧视', '宗教争议', 
            '教派对立', '宗教仇恨', '宗教迫害'
        ],
        'adult': [
            '色情内容', '成人服务', '性服务', '色情网站', 
            '成人娱乐', '涉黄内容', '不当内容'
        ],
        'finance_sensitive': [
            '股票内幕', '市场操纵', '非法集资', '金融诈骗', 
            '洗钱活动', '高利贷', '非法博彩', '金融犯罪'
        ],
        'sensitive_topics': [
            '政治敏感话题', '社会敏感事件', '历史争议', '民族问题',
            '领土争端', '国际制裁', '外交纠纷', '敏感人物'
        ]
    }
    
    # 安全的替代词汇
    SAFE_ALTERNATIVES = {
        'politics': [
            '公共政策研究', '社会治理', '公共管理', '社会发展', 
            '经济政策', '社会政策', '公共服务', '社会创新'
        ],
        'news': [
            '行业动态', '技术发展', '市场趋势', '科研进展',
            '商业资讯', '产业分析', '创新案例', '发展报告'
        ],
        'research': [
            '学术研究', '科学发现', '技术突破', '理论进展',
            '实验结果', '数据分析', '方法论', '案例研究'
        ],
        'business': [
            '商业模式', '市场分析', '竞争策略', '商业趋势',
            '企业管理', '营销策略', '品牌建设', '客户体验'
        ],
        'technology': [
            '人工智能', '机器学习', '大数据', '云计算',
            '物联网', '区块链', '5G技术', '数字化转型'
        ]
    }

    @classmethod
    def check_query_safety(cls, query: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查查询的安全性
        
        Args:
            query: 用户输入的查询字符串
            
        Returns:
            Tuple[是否安全, 发现的敏感词, 建议的替代词]
        """
        query_lower = query.lower()
        found_risky = []
        suggestions = []
        
        # 检查敏感关键词
        for category, keywords in cls.RISKY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_risky.append(keyword)
        
        # 如果发现敏感词，提供替代建议
        if found_risky:
            # 根据查询内容推荐替代词
            if any(word in query_lower for word in ['新闻', 'news', '动态', '最新']):
                suggestions.extend(cls.SAFE_ALTERNATIVES['news'])
            elif any(word in query_lower for word in ['研究', 'research', '分析']):
                suggestions.extend(cls.SAFE_ALTERNATIVES['research'])
            elif any(word in query_lower for word in ['商业', 'business', '市场']):
                suggestions.extend(cls.SAFE_ALTERNATIVES['business'])
            elif any(word in query_lower for word in ['技术', 'technology', '科技']):
                suggestions.extend(cls.SAFE_ALTERNATIVES['technology'])
            else:
                # 通用安全建议
                suggestions.extend(cls.SAFE_ALTERNATIVES['research'][:2])
                suggestions.extend(cls.SAFE_ALTERNATIVES['technology'][:2])
        
        is_safe = len(found_risky) == 0
        return is_safe, found_risky, suggestions[:5]  # 限制建议数量

    @classmethod
    def preprocess_query_for_safety(cls, query: str) -> str:
        """
        预处理查询，自动替换或优化可能有问题的词汇
        
        Args:
            query: 原始查询
            
        Returns:
            str: 处理后的查询
        """
        try:
            processed_query = query
            
            # 智能替换可能敏感的词汇
            safe_replacements = {
                '最新政治': '最新政策发展',
                '政府官员': '公共管理',
                '政治动态': '政策动态',
                '政治新闻': '政策新闻',
                '军事冲突': '国际形势',
                '宗教争议': '文化研究',
                '宗教冲突': '文化差异研究',
                '股票内幕': '市场分析',
                '金融诈骗': '金融安全',
                '投资诈骗': '投资风险',
            }
            
            # 执行智能替换
            for sensitive, safe in safe_replacements.items():
                if sensitive in processed_query:
                    processed_query = processed_query.replace(sensitive, safe)
            
            return processed_query
            
        except Exception as e:
            # 如果处理失败，返回原查询
            return query
    
    @classmethod
    def suggest_safe_query(cls, original_query: str) -> str:
        """
        为不安全的查询建议安全的替代版本
        
        Args:
            original_query: 原始查询
            
        Returns:
            str: 建议的安全查询
        """
        is_safe, risky_words, suggestions = cls.check_query_safety(original_query)
        
        if is_safe:
            return original_query
        
        # 尝试替换敏感词
        safe_query = original_query
        
        # 简单的词汇替换
        replacements = {
            '政治': '公共政策',
            '政府': '公共部门',
            '暴力': '社会现象',
            '冲突': '争议',
            '战争': '历史事件',
            '宗教': '文化传统',
            '最新新闻': '行业动态',
            '新闻动态': '发展趋势',
            '时事': '社会发展'
        }
        
        for risky, safe in replacements.items():
            safe_query = safe_query.replace(risky, safe)
        
        return safe_query

    @classmethod
    def get_safety_tips(cls) -> Dict[str, List[str]]:
        """
        获取内容安全建议
        
        Returns:
            Dict: 分类的安全建议
        """
        return {
            'recommended_topics': [
                '科技发展趋势',
                '学术研究进展',
                '商业模式创新',
                '经济发展分析',
                '教育发展动态',
                '健康医疗进展',
                '环境保护技术',
                '文化交流活动'
            ],
            'query_tips': [
                '使用具体的技术术语',
                '聚焦于学术或商业角度',
                '避免主观性强的表达',
                '使用中性的描述词汇',
                '关注数据和事实分析'
            ],
            'avoid_topics': [
                '政治敏感话题',
                '宗教争议内容',
                '暴力相关描述',
                '成人或不当内容',
                '极端观点表达'
            ]
        }

    @classmethod
    def format_safety_suggestion(cls, original_query: str) -> Dict[str, any]:
        """
        格式化安全建议响应
        
        Args:
            original_query: 原始查询
            
        Returns:
            Dict: 格式化的建议响应
        """
        is_safe, risky_words, suggestions = cls.check_query_safety(original_query)
        safe_query = cls.suggest_safe_query(original_query)
        safety_tips = cls.get_safety_tips()
        
        return {
            'is_safe': is_safe,
            'original_query': original_query,
            'safe_query': safe_query,
            'risky_words': risky_words,
            'alternative_suggestions': suggestions,
            'safety_tips': safety_tips,
            'message': (
                '查询内容安全' if is_safe 
                else f'检测到{len(risky_words)}个可能的敏感词汇，建议使用更中性的表达'
            )
        }
