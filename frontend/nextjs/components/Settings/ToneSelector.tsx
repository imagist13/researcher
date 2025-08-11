import React, { ChangeEvent } from 'react';

interface ToneSelectorProps {
  tone: string;
  onToneChange: (event: ChangeEvent<HTMLSelectElement>) => void;
}
export default function ToneSelector({ tone, onToneChange }: ToneSelectorProps) {
  return (
    <div className="form-group">
      <label htmlFor="tone" className="agent_question">语调 </label>
      <select 
        name="tone" 
        id="tone" 
        value={tone} 
        onChange={onToneChange} 
        className="form-control-static"
        required
      >
        <option value="Objective">客观 - 公正无偏见地呈现事实和发现</option>
        <option value="Formal">正式 - 遵循学术标准，使用精练的语言和结构</option>
        <option value="Analytical">分析性 - 批判性评估和详细检查数据与理论</option>
        <option value="Persuasive">说服性 - 说服读者接受特定观点或论证</option>
        <option value="Informative">信息性 - 提供清晰全面的主题信息</option>
        <option value="Explanatory">解释性 - 阐明复杂概念和过程</option>
        <option value="Descriptive">描述性 - 详细描绘现象、实验或案例研究</option>
        <option value="Critical">批判性 - 判断研究及其结论的有效性和相关性</option>
        <option value="Comparative">比较性 - 对比不同理论、数据或方法以突出差异和相似性</option>
        <option value="Speculative">推测性 - 探索假设和潜在影响或未来研究方向</option>
        <option value="Reflective">反思性 - 考虑研究过程和个人见解或经验</option>
        <option value="Narrative">叙述性 - 通过故事来阐述研究发现或方法</option>
        <option value="Humorous">幽默性 - 轻松有趣，通常使内容更具亲和力</option>
        <option value="Optimistic">乐观性 - 突出积极发现和潜在益处</option>
        <option value="Pessimistic">悲观性 - 关注局限性、挑战或负面结果</option>
        <option value="Simple">简单性 - 为年轻读者撰写，使用基础词汇和清晰解释</option>
        <option value="Casual">随意性 - 对话式和轻松的风格，便于日常阅读</option>
      </select>
    </div>
  );
}