import type { AestheticInput, InputFeature, ReportResponse } from "../types/aesthetic";

export const starterInputs: AestheticInput[] = [
  {
    id: "input_001",
    type: "image",
    title: "灰蓝色室内图",
    fileUrl: "mock://quiet-room",
    description: "低饱和、人物缺席、空间留白明显。"
  },
  {
    id: "input_002",
    type: "text",
    title: "空房间片段",
    contentText: "房间里只剩下下午的光，回声很轻，像某种被放慢的秩序。",
    description: "文本偏向低密度观察，而不是完整叙事。"
  },
  {
    id: "input_003",
    type: "image",
    title: "静物构图",
    fileUrl: "mock://still-life",
    description: "少量物体、柔和明暗、中心偏移。"
  }
];

function featureFor(input: AestheticInput, index: number): InputFeature {
  const isText = input.type === "text";
  return {
    inputId: input.id,
    featureType: input.type,
    promptVersion: isText ? "text_features.extract.v1" : "image_features.extract.v1",
    lowLevelFeatures: {
      saturation: {
        value: index % 2 === 0 ? "low" : "medium-low",
        confidence: 0.76,
        evidence: [isText ? "文本使用安静、低明度的意象" : "画面整体以低饱和色块为主"]
      },
      density: {
        value: "low",
        confidence: 0.72,
        evidence: [isText ? "叙事更接近片段观察" : "画面元素数量较少，留白明显"]
      },
      presence: {
        value: "person_absent",
        confidence: 0.68,
        evidence: [isText ? "描述中没有明确人物行动" : "主体更偏空间或物体而非人物"]
      }
    },
    sampleEvidence: [input.title, input.description ?? input.contentText ?? "当前样本"]
  };
}

export function mockReport(inputs: AestheticInput[]): ReportResponse {
  const selectedInputs = inputs.length >= 3 ? inputs : starterInputs;
  const lowLevelFeatures = selectedInputs.map(featureFor);
  const evidenceRefs = selectedInputs.slice(0, 3).map((input) => input.id);

  return {
    reportId: "report_mock_v0",
    title: "近期审美观察报告",
    summary: "这组输入呈现出低饱和、低密度、人物存在感较弱的共同倾向。系统只把它视为本次样本中的可观察结构，而不是人格判断。",
    lowLevelFeatures,
    similarityGroups: [
      {
        groupId: "group_001",
        name: "安静低密度组",
        inputIds: evidenceRefs,
        commonFeatures: ["low_saturation", "low_density", "person_absent"],
        uncertainty: "样本数量较少，该分组只表示本次输入中的相似结构，不代表长期偏好。"
      }
    ],
    possibleInterpretations: [
      {
        id: "interpretation_001",
        name: "克制空间感",
        confidence: 0.71,
        evidenceRefs,
        uncertainty: "也可能只是当前上传样本主题较集中。"
      },
      {
        id: "interpretation_002",
        name: "低刺激叙事",
        confidence: 0.64,
        evidenceRefs: evidenceRefs.slice(0, 2),
        uncertainty: "文本和图像样本混合时，该解释需要更多输入验证。"
      }
    ],
    insights: [
      {
        insightId: "insight_001",
        title: "你近期可能更容易被安静、低密度的结构吸引",
        observation: "多个输入都出现低饱和、低元素密度和人物缺席。",
        evidenceRefs,
        interpretation: "这可能说明你现在更关注留白、秩序和克制的空间感。",
        uncertainty: "它不是心理诊断，只是对本次样本的审美结构观察。",
        confidence: 0.72
      },
      {
        insightId: "insight_002",
        title: "样本中有一种弱叙事、强氛围的倾向",
        observation: "文字和图像都更强调状态、光线和空间，而不是明确事件。",
        evidenceRefs: evidenceRefs.slice(0, 2),
        interpretation: "这可能表示你对开放解释空间的作品更有耐心。",
        uncertainty: "如果后续样本加入人物或强情节内容，这条洞察可能会改变。",
        confidence: 0.66
      }
    ],
    disclaimer: "这是一份基于当前输入的审美观察，不是人格诊断、心理评估或长期画像。"
  };
}
