import { apiClient } from "./apiClient";

export interface SourceEvidence {
  docIds: string[];
  note: string;
}

export interface AestheticConcept {
  id: string;
  slug: string;
  label: string;
  description: string;
  featureTags: string[];
  sourceRefs: string[];
  createdAt?: string | null;
}

export interface ConceptRelation {
  id: string;
  fromConceptId: string;
  toConceptId: string;
  predicate: "related_to" | "contrasts_with" | "example_of";
  sourceEvidence: SourceEvidence;
  createdAt?: string | null;
}

export interface ConceptListResponse {
  concepts: AestheticConcept[];
  total: number;
}

export interface ConceptDetailResponse {
  concept: AestheticConcept;
  outgoing: ConceptRelation[];
  incoming: ConceptRelation[];
}

export interface GraphEdgeView {
  relation: ConceptRelation;
  fromLabel: string;
  toLabel: string;
}

export interface KnowledgeGraphResponse {
  rootConceptId: string;
  concepts: AestheticConcept[];
  edges: GraphEdgeView[];
  disclaimer: string;
}

export interface KnowledgeChunkSummary {
  docId: string;
  title: string;
  snippet: string;
  featureTags: string[];
  source: string;
}

export interface KnowledgeChunkListResponse {
  chunks: KnowledgeChunkSummary[];
  total: number;
}

export function listConcepts(featureTag?: string) {
  const query = featureTag ? `?featureTag=${encodeURIComponent(featureTag)}` : "";
  return apiClient<ConceptListResponse>(`/api/aesthetic-knowledge/concepts${query}`);
}

export function getConceptDetail(conceptId: string) {
  return apiClient<ConceptDetailResponse>(`/api/aesthetic-knowledge/concepts/${conceptId}`);
}

export function getKnowledgeGraph(conceptId: string) {
  return apiClient<KnowledgeGraphResponse>(
    `/api/aesthetic-knowledge/graph?conceptId=${encodeURIComponent(conceptId)}`,
  );
}

export function listKnowledgeChunks() {
  return apiClient<KnowledgeChunkListResponse>("/api/aesthetic-knowledge/chunks");
}
