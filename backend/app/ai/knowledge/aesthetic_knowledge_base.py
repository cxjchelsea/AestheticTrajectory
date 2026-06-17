from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    doc_id: str
    title: str
    snippet: str
    feature_tags: frozenset[str]
    source: str


AESTHETIC_KNOWLEDGE_CHUNKS: tuple[KnowledgeChunk, ...] = (
    KnowledgeChunk(
        doc_id="kb_low_saturation_space",
        title="低饱和与留白结构",
        snippet="低饱和色块和较多留白常形成克制、距离感较强的视觉结构，更适合描述空间气质，而不是判断用户性格。",
        feature_tags=frozenset({"saturation=low", "density=low"}),
        source="project-aesthetic-knowledge-v1",
    ),
    KnowledgeChunk(
        doc_id="kb_medium_low_saturation",
        title="中低饱和的柔和过渡",
        snippet="中低饱和常见于柔和过渡和弱对比场景，适合作为解释语言中的“温和结构”参考，不应直接写成用户偏好结论。",
        feature_tags=frozenset({"saturation=medium-low"}),
        source="project-aesthetic-knowledge-v1",
    ),
    KnowledgeChunk(
        doc_id="kb_person_absent_composition",
        title="非人物中心的观察",
        snippet="当输入更偏空间、物体或片段意象而非明确人物行动时，解释应优先围绕构图、材质和氛围，而不是推断主体人格。",
        feature_tags=frozenset({"presence=person_absent"}),
        source="project-aesthetic-knowledge-v1",
    ),
    KnowledgeChunk(
        doc_id="kb_low_density_fragment",
        title="低密度与片段叙事",
        snippet="元素较少、留白明显的结构更接近片段观察，适合谨慎描述局部倾向，而不是扩展为稳定人格画像。",
        feature_tags=frozenset({"density=low", "presence=person_absent"}),
        source="project-aesthetic-knowledge-v1",
    ),
)
