import React, { useState, useEffect } from 'react';
import { generationService } from '../services/generation';
import { UserRole } from '../services/auth';
import { modelService, ModelInfo } from '../services/models';

const SAMPLE_INPUT = `
INTRODUCTION
The non-Hodgkin lymphoma subtype of marginal zone lymphoma represents a group of lymphomas that have been historically classified together because they appear to arise from post-germinal center marginal zone B cells and share a similar immunophenotype: positive for B cell markers CD19, CD20, and CD22, and negative for CD5, CD10, and usually CD23.
Several marginal zone lymphoma subtypes are recognized in the World Health Organization classification of lymphoid neoplasms:
●Extranodal marginal zone lymphoma of mucosa associated lymphoid tissue (MALT lymphoma)
●Primary cutaneous marginal zone lymphoma
●Nodal marginal zone lymphoma
●Splenic marginal zone lymphoma
Extranodal marginal zone lymphoma (EMZL) arises in a number of epithelial tissues, including the stomach, salivary gland, lung, small bowel, thyroid, ocular adnexa, skin, and elsewhere. While it tends to remain localized to the tissue of origin for long periods of time, it is a clonal B cell neoplasm that frequently recurs locally and has potential for systematic spread and transformation to an aggressive B cell lymphoma.
Extranodal marginal zone lymphoma (EMZL) has also been called low grade B cell lymphoma of mucosa associated lymphoid tissue (MALT), "MALT-type lymphoma," "MALT lymphoma," "MALToma," and "pseudo-lymphoma."
Other colloquial terms are sometimes used for EMZL arising in specific tissues. As examples, EMZL of the lung is sometimes referred to as bronchial-associated lymphoid tissue (BALT) lymphoma (image 1).
Immunoproliferative small intestinal disease (IPSID) lymphoma is a variant of EMZL that secretes immunoglobulin alpha heavy chains. IPSID has also been called alpha heavy chain disease, Mediterranean lymphoma, and Seligmann disease.
PATHOGENESIS
Extranodal marginal zone lymphoma (EMZL) is a clinically indolent non-Hodgkin lymphoma postulated to arise from post-germinal center memory B cells with the capacity to differentiate into marginal zone cells and plasma cells . Many cases of EMZL develop in the setting of chronic immune stimulation, often due to bacterial, viral, or autoimmune stimuli. The prototypical example is the association of Helicobacter pylori infection with chronic gastritis and the development of gastric EMZL. The association of EMZL with autoimmune diseases and infectious agents is presented in more detail below.
One suggested pathogenic mechanism is that chronic inflammation leads to the local accumulation and proliferation of antigen-dependent B cells and T cells. With time, B cell clones emerge that still depend on the antigen-stimulated immune response for growth and survival bearing, oncogenic mutations that convey a local growth advantage. At this stage, the proliferation is monoclonal but not yet able to spread beyond the site of inflammation. With the acquisition of additional mutations, the tumor becomes antigen-independent and capable of systemic spread and may undergo large cell transformation.
Four recurrent chromosomal translocations have been found in EMZL:
●t(11;18)(q21;q21)
●t(14;18)(q32;q21)
●t(1;14)(p22;q32)
●t(3;14)(p13;q32)
In normal B and T cells, signals produced by the interaction of antigen with antigen receptors on the cell surface cause the protein BCL10 (B cell leukemia/lymphoma 10) to bind to the MALT1 (MALT lymphoma-associated translocation-1) protein. This triggers additional events that result in the activation of nuclear factor kappa B (NF-kB), a transcription factor that turns on a set of genes that promote B cell survival . The t(11;18), t(14;18), and t(1;14) translocations all result in pathophysiologic increases in the activation of NF-kB through the BCL10/MALT1 signaling complex, and in doing so enhance the survival of EMZL cells .
At a genomic level, the t(11;18) translocation fuses the apoptosis inhibitor-2 (AIP) gene on chromosome 11 (variously called API2 or IAP2) with the MALT1 gene on chromosome 18 , while the t(14;18)(q32;q21) fuses MALT1 with the IgH gene. The rare t(1;14)(p22;q32) fuses the coding sequence of BCL10 on chromosome 1 to the IgH promoter/enhancer elements . These varied events all result in over-expression of BCL10, which causes cellular transformation , and provides a survival advantage to the neoplastic B cells. Nuclear expression of BCL10 or NF-kB in gastric EMZL, determined by immunohistochemistry, is associated with resistance of gastric EMZL to antibiotic therapy, even in those tumors that lack the t(11;18) .
The other known translocation, t(3;14)(p13;q32), fuses the FOXP1 gene on chromosome 3 to the IGH gene and results in increased nuclear levels of the FOXP1 transcription factor . The contribution of FOXP1 to EMZL is unclear, but overexpression of FOXP1 in transgenic mice promotes the expansion of marginal zone B cells at the expense of germinal center B cells, suggesting that it interferes with normal B cell maturation . Conversely, loss-of-function studies in knockout mice show that FOXP1 loss leads to reduced B cell numbers, impaired T cell independent antibody production, and decreased B cell survival, possibly because of lowered expression of BCL-XL, an anti-apoptotic member of the BCL2 family . One study found high nuclear FOXP1 to be linked to poor outcome in EMZL . Of further interest, tumors with FOXP1 translocation appear to transform to diffuse large B cell lymphoma frequently, whereas those with the t(11;18) do so rarely, if ever .

EPIDEMIOLOGY
Extranodal marginal zone lymphoma (EMZL) is a relatively uncommon subtype of non-Hodgkin lymphoma. It is mainly seen in adults with a median age at diagnosis of 66 years .
EMZL occurs in all populations worldwide, but the exact incidence is not known. The incidence appears to be lower in resource-limited compared with resource-abundant countries , but epidemiologic data are limited in countries that do not have the resources needed to make an accurate diagnosis. As a result, most epidemiologic data come from retrospective analyses of patients treated at major centers in the United States and Europe.
In the United States as a whole, EMZL accounts for 5 to 10 percent of non-Hodgkin lymphomas overall but makes up approximately half of lymphomas in particular sites, such as the stomach , ocular adnexa , and lung .
In the United States, EMZL has an estimated incidence of 18.3 cases per 1 million person-years . The incidence has been stable over time and varies by population, being highest in the non-Hispanic White population and lowest in the Black population . EMZL occurs equally among males and females. Disparities are seen by site, with males more commonly having involvement of the stomach, small intestine, skin, and kidney, and females more commonly having involvement of the salivary gland, soft tissue, and thyroid. Some of these disparities are explained by differences in the incidence of Sjögren's disease and Hashimoto's thyroiditis, both of which are more common in females than in males and which predispose to EMZL of the salivary gland and thyroid, respectively.
Immunoproliferative small intestinal disease (IPSID, Mediterranean lymphoma, alpha heavy chain disease) is a variant of EMZL that primarily occurs in young adults in the Middle East, North and South Africa, and the Far East .
CLINICAL FEATURES
Presenting features — The majority of patients with extranodal marginal zone lymphoma (EMZL) present with symptoms due to localized (stage I or II) involvement of glandular epithelial tissues of various sites.
The stomach is the most frequent site of involvement (picture 1 and picture 2), but EMZL can involve other parts of the gut, the ocular adnexa, lung, lacrimal and salivary glands, thyroid, breast, synovium, dura, skin, and soft tissues .
The clinical presentation differs depending on the tissue involved. As examples:
●Gastric – Patients with gastric EMZL may present with symptoms of gastroesophageal reflux disease, epigastric pain or discomfort, anorexia, weight loss, or occult gastrointestinal bleeding .
●Ocular adnexa – Patients with EMZL of the ocular adnexa may present with a slow growing mass, eye redness, and epiphora (excessive eye watering) .
●Salivary gland – Patients with EMZL of the salivary gland may present with a slow growing mass; a minority will have bilateral involvement .
●Skin – Patients with primary cutaneous marginal zone lymphoma present with red to violaceous papules, plaques, or nodules localized preferentially on the trunk or upper extremities.
●Lung – Patients with EMZL of the lung may present with asymptomatic lung nodules and/or air space consolidation on imaging .
●Small intestine – Patients with EMZL of the small intestine (immunoproliferative small intestinal disease, IPSID) may present with intermittent diarrhea, colicky abdominal pain, and symptoms related to malabsorption .
EMZL disseminate to other sites of mucosa-associated lymphoid tissue, lymph nodes, or marrow in about 30 percent of cases . It had been thought that this was often a late event; however, increasing evidence suggests that disseminated disease is present at diagnosis in approximately one-third of cases .
The peripheral blood is usually not initially involved; however, some series report lymph node or bone marrow involvement in up to 25 percent . Our own clinical experience suggests that this occurs less frequently. Systemic "B symptoms" (ie, fevers, night sweats, weight loss) are uncommon (<5 percent) .
A monoclonal gammopathy is found in 27 to 36 percent of patients with EMZL, and correlates with plasmacytic differentiation as well as with advanced disease, including involvement of lymph nodes and/or bone marrow . Rarely, EMZL may be associated with localized or systemic AL amyloidosis .
Disease associations — Increasing evidence suggests that EMZL is related to chronic immune reactions driven by bacterial, viral, or autoimmune stimuli. Proliferation of the cells of marginal zone lymphoma at certain sites appears to depend on the presence of activated, antigen-driven T cells. As such, patients with EMZL may also display evidence of the diseases described below.
Autoimmune disorders — Many patients with EMZL have a history of autoimmune disease (eg, Sjögren's disease, systemic lupus erythematosus, or relapsing polychondritis, Hashimoto's thyroiditis), with or without coexisting infections .
As an example, a pooled analysis of individual data from 12 case-control studies reported the following associations with EMZL :
●Sjögren's disease was associated with a 6.6-fold increased risk for non-Hodgkin lymphoma overall, a 30-fold increase in risk for marginal zone lymphoma, and a 1000-fold increased risk of parotid gland EMZL.
●Systemic lupus erythematosus was associated with a 2.7-fold increase in risk for non-Hodgkin lymphoma overall and a 7.5-fold increased risk for marginal zone lymphoma.
These lymphomas are thought to arise from acquired mucosa associated lymphoid tissue that develops secondary to autoimmune stimulation in these sites. Specifics on the various autoimmune disorders are presented separately.
Helicobacter pylori — An overwhelming body of evidence has shown that the development of gastric EMZL is frequently due to the clonal expansion of B cells that accompanies chronic gastritis in the presence of Helicobacter pylori. H. pylori-induced gastritis first leads to the accumulation of CD4+ lymphocytes and mature B cells in the gastric lamina propria. Antigens derived from H. pylori drive the activation of T cells, B cell proliferation, and lymphoid follicle formation, which if persistent can evolve into a monoclonal lymphoma.
Therapy directed at the H. pylori infection results in regression of most early lesions and has become the treatment of choice for most patients. Most patients (>90 percent) with gastric EMZL are H. pylori positive.
Chlamydia psittaci — An association between psittacosis and ocular adnexal marginal zone lymphoma (OAL) has been described, suggesting that Chlamydia psittaci may be a causative agent . There are conflicting reports of this association across geographic regions and in studies from the same regions . Antibiotics have shown variable efficacy against OAL. The use of antibiotics in OAL is discussed in more detail separately.
Most of the evidence supporting this association comes from Italy where OAL has been associated with C. psittaci infection in 80 percent of the cases . Treatment of Chlamydia infection with the antibiotic doxycycline or clarithromycin has produced tumor response in some cases . However, this organism was not seen in tumor specimens from a number of other countries, including Japan, France, the Netherlands, and the United States, and in only 2 of 26 cases from Cuba .
A meta-analysis of available reports indicates striking variability in the association between this infection and OAL across geographic regions, as well as variability in its response to treatment with antibiotics .
Campylobacter jejuni — Immunoproliferative small intestinal disease (IPSID, Mediterranean lymphoma, alpha heavy chain disease) is a variant of EMZL that primarily occurs in young adults in the Middle East, North and South Africa, and the Far East . Clinical features include intermittent diarrhea, colicky abdominal pain, and symptoms related to malabsorption. Upper endoscopy usually shows diffuse abnormalities from the second part of the duodenum through the upper jejunum consisting of thickening, erythema, and nodularity of the mucosal folds. Biopsy shows an infiltrate of centrocyte-like cells and plasma cells. An alpha heavy chain protein without an associated light chain may be detected in the serum.
Observational studies suggest an association with Campylobacter jejuni infection and there have been some reports of responses to antibiotics directed at this infection .
Borrelia afzelii — There is controversy regarding a possible link between solitary cutaneous marginal zone lymphoma and Borrelia afzelii infection, a species of Borrelia burgdorferi associated with Lyme disease almost exclusively found in Europe.
Observational studies suggest that treatment with antibiotic therapy may cure a proportion of patients with B. afzelii-associated cutaneous lymphoma. This is discussed in more detail separately.
Achromobacter xylosoxidans — The role of infection in pulmonary EMZL remains uncertain. A potential link between pulmonary EMZL and Achromobacter xylosoxidans infection was suggested in one study with higher rates of A. xylosoxidans within EMZL lung biopsy specimens than within control tissue . However, one follow-up study that used sequencing of nonhost DNA and RNA isolated from pulmonary EMZL failed to confirm the association with A. xylosoxidans and also failed to detect evidence of an association with other infectious agents .

PATHOLOGIC FEATURES
Morphology — Extranodal marginal zone lymphoma (EMZL) reproduces the morphologic features of normal mucosa associated lymphoid tissue (MALT). Reactive follicles are usually present, with the neoplastic cells occupying the marginal zone and/or the interfollicular region. Occasional follicles may be "colonized" by neoplastic cells. An important diagnostic clue is the effacement of normal mucosal architecture, which is not usually seen in reactive lymphoid proliferations.
The morphology of the malignant clone is variable. The involved tissue demonstrates a polymorphous infiltrate of small lymphocytes, marginal zone (centrocyte-like) B cells, monocytoid B cells, and plasma cells, as well as less frequent large activated cells (centroblast- or immunoblast-like) (picture 3 and picture 4) . While these large cells are typically present, they are by definition in the minority. In some tumors, medium-sized cells resembling centrocytes predominate and are characterized by elongated or cleaved nuclei, inconspicuous nucleoli, and scant pale cytoplasm. In other tumors, the malignant cells resemble small lymphocytes or have plasmacytic differentiation.
In tissues with epithelial linings, the tumor cells typically infiltrate the epithelium, forming so-called "lymphoepithelial lesions."
Immunophenotype — The immunophenotype is usually confirmed by immunohistochemistry but may also be demonstrated using flow cytometry. The key immunophenotypic findings are the demonstration of clonality (light chain restriction), confirmation of B cell origin (presence of B cell markers and lack of T cell markers), and exclusion of other small B cell lymphomas such as small lymphocytic lymphoma and mantle cell lymphoma (which are both CD5+) and follicular lymphoma (which is CD10+, CD43-, CD11c-, and usually cytoplasmic Ig-) .

EMZL tumor cells express surface membrane immunoglobulin (IgM>IgG>IgA) and lack IgD; 40 to 60 percent have monotypic cytoplasmic immunoglobulin, indicating plasmacytic differentiation . They express B cell-associated antigens (CD19, CD20, CD22, CD79a) (picture 4) and complement receptors (CD21 and CD35), and are usually negative for CD5, CD10, CD23, BCL6, and cyclin D1.
Genetic features
Immunoglobulin gene rearrangement — Immunoglobulin genes are rearranged, and the variable region has a high degree of somatic mutation as well as intraclonal diversity, consistent with a post-germinal center stage of B cell development . The rearranged immunoglobulin heavy chain variable segments are often those that produce autoantibodies, consistent with studies showing that the antibodies produced by the tumor cells have specificity against self-antigens . The CCND1 (cyclin D1) and BCL2 genes are not rearranged .
Chromosomal abnormalities — EMZL frequently have chromosomal abnormalities, but there is no single chromosomal change that is diagnostic . The most commonly reported findings are:
●Trisomy 3 (60 percent)
●t(11;18)(q21;q21) (25 to 40 percent)
●t(14;18)(q32;q21)
●t(1;14)(p22;q32)
●t(3;14)(p13;q32)
Other chromosomal abnormalities have also been reported in EMZL, including isochromosome 17q and 2p11 translocations , which are presently of uncertain pathogenic significance.
Chromosomal studies may be useful for identifying subgroups of patients who may or may not respond to treatment. Some studies suggest that t(11;18) may characterize a subgroup of EMZL that are less likely to transform to high grade lymphoma . In addition, a number of observations suggest that the presence of trisomy 3, BCL10 gene mutation, and/or t(11;18) might identify those patients with gastric EMZL who are less likely to benefit from therapy directed at H. pylori .
Molecular genetic findings — Sequencing of MALT lymphoma genomes has revealed recurrent mutations in genes encoding proteins that participate in several different signaling pathways or that function as epigenetic regulators.
One of the most commonly mutated genes, particularly in ocular and salivary gland MALT lymphoma, is TNFAIP3, a negative regulator of NF-kB signaling . Mutations in genes encoding components of the Notch pathway, which regulates marginal zone B cell differentiation, are found in a minority of cases . Epigenetic regulators that are commonly mutated include CREBBP and KMT2C, which catalyze acetylation of histones and nonhistone proteins and histone methylation, respectively . Of interest, thyroid EMZL is particularly likely to have mutations in genes that regulate host T cell responses, such as PDL1 and TNFRSF14 .

DIAGNOSIS
The diagnosis of extranodal marginal zone lymphoma (EMZL) of mucosa associated lymphoid tissue (MALT) is made based upon morphologic, immunophenotypic, and genetic analysis of biopsy material taken from an affected site, interpreted within the clinical context.
Clinicians should aim to attain the largest biopsy specimen possible, as small biopsies and fine needle aspirates may not provide adequate tissue for diagnosis. As an example, conventional pinch biopsies performed during endoscopy may miss the diagnosis of gastric EMZL, since the tumor can infiltrate the submucosa without affecting the mucosa; this problem is most likely to occur when no obvious mass is present. Jumbo biopsies, snare biopsies, biopsies within biopsies ("well technique"), and needle aspiration can all serve to increase the yield in such cases. Endoscopic ultrasound-guided fine needle aspiration biopsy or endoscopic submucosal resection may provide even greater diagnostic capability.
As described in more detail above, morphologic review reveals a polymorphous infiltrate of small cells with associated reactive-appearing follicles. While some large cells are typically present, they are by definition in the minority. On immunophenotype, cells express the B cell markers CD19, CD20, and CD22, and do not express CD5, CD10, and CD23. Detection of a monoclonal immunoglobulin by flow cytometry or immunohistochemistry is helpful in confirming the neoplastic nature of the proliferation. Molecular diagnostic analysis consisting of polymerase chain reaction (PCR)-based analysis of IGH gene rearrangements can also be very helpful in distinguishing EMZL from reactive proliferations. While not diagnostic, detection of trisomy 3 or t(11;18) is supportive of the diagnosis.

DIFFERENTIAL DIAGNOSIS
Reactive lesions — Extranodal marginal zone lymphoma (EMZL) often develops within the context of chronic immune reactions driven by bacterial, viral, or autoimmune stimuli. Reactive lesions are usually limited to the follicle, whereas the neoplastic cells of EMZL extend outside of the follicle and may destroy surrounding tissue . Most cases of EMZL can be distinguished from reactive lesions by the demonstration of immunoglobulin light chain restriction or clonal IGH rearrangements by molecular techniques.
Nodal and splenic marginal zone lymphoma — Some cases of EMZL can disseminate to nodal sites, spleen, and bone marrow . In such cases it may be unclear exactly where the disease originated. A diagnosis of nodal marginal zone lymphoma is favored if there is widespread nodal involvement, even in the setting of splenic enlargement and/or minimal extranodal involvement. In contrast, EMZL is favored when the extranodal involvement is prominent and nodal involvement is localized. In addition, a diagnosis of EMZL rather than splenic marginal zone lymphoma is favored in cases with t(11;18), t(14;18), t(1;14), or t(3;14).
Other B cell neoplasms — EMZL must be distinguished from other B cell neoplasms that may involve extranodal sites. These include:
●Diffuse large B cell lymphoma (DLBCL) – Both DLBCL and EMZL may have a primary extranodal presentation. DLBCL is more aggressive clinically with rapid growth. The differentiation between EMZL and DLBCL is made primarily based upon morphologic features.
Tumors that otherwise resemble EMZL that have large clusters or sheets of large cells (centroblast- or immunoblast-like cells) have a worse prognosis . These tumors are cytogenetically, biologically, and clinically different from EMZL and should be given a diagnosis of DLBCL. In addition, the term "high grade MALT lymphoma" should be avoided for large B cell lymphomas in mucosa associated lymphoid tissue, since it may lead to inappropriate undertreatment.
Interestingly, neither trisomy 3 nor t(11;18)(q21;q21) is common in primary large B cell lymphomas of the gastrointestinal tract .
●Small lymphocytic lymphoma (SLL) – SLL, the solid tumor variant of the more common chronic lymphocytic leukemia (CLL), is composed of small lymphocytes on morphologic review. SLL is predominantly node-based, with extranodal disease only appearing later in the course. Immunophenotypically, SLL cells co-express CD5 and CD23 whereas EMZL cells do not.
●Mantle cell lymphoma (MCL) – Both EMZL and MCL are neoplasms of small- to medium-sized B lymphocytes. In addition, both can involve the gastrointestinal tract. On immunophenotype, MCL expresses CD5 and cyclin D1 (usually due to the presence of a (11;14) translocation), while EMZL does not express these markers and is t(11;14) negative.
●Follicular lymphoma (FL) – Reactive follicles are usually present in EMZL and occasionally these follicles may be "colonized" by marginal zone or monocytoid cells. Prominent follicles are also seen in FL, which occasionally involves the gut, particularly the small bowel; however, these two entities can usually be distinguished by immunophenotype.
FL typically expresses CD10 and BCL6, does not express CD43, and only rarely demonstrates plasmacytic differentiation, which is seen in about 40 percent of EMZL. Also, FL is strongly associated with t(14;18) rearrangements involving the BCL2 gene, which are absent in EMZL.

SUMMARY
●Pathogenesis – Extranodal marginal zone lymphoma (EMZL) is a clinically indolent non-Hodgkin lymphoma postulated to arise from post-germinal center memory B cells with the capacity to differentiate into marginal zone cells and plasma cells. Several translocations resulting in increased activation of nuclear factor kappa B (NF-kB) have been implicated in the pathogenesis. These translocations can occur with or without a coexisting chronic immune stimulation.
●Epidemiology – EMZL constitute 5 to 10 percent of all non-Hodgkin lymphomas overall, but make up approximately half of lymphomas in particular sites, such as the stomach, ocular adnexa, and lung.
●Clinical features – The clinical presentation of EMZL differs depending on the tissue involved. The majority of patients present with symptoms due to localized involvement of various sites, including the stomach, other parts of the gut, salivary gland, lung, small bowel, thyroid, ocular adnexa, skin, and soft tissue. Systemic symptoms are uncommon.
EMZL may be related to chronic immune stimulation, due to bacterial, viral, or autoimmune stimuli. Patients with EMZL may also display evidence of autoimmune disorders or infections.
•The following associations between EMZL at certain sites and particular infections have been proposed: Helicobacter pylori (gastric), Chlamydia psittaci (ocular adnexa), Campylobacter jejuni (small intestine), Borrelia afzelii (skin), and Achromobacter xylosoxidans (lung). Of these, the association with H. pylori is the best established.
•The most commonly associated autoimmune disorders are Sjögren's disease (parotid EMZL), systemic lupus erythematosus, relapsing polychondritis, and Hashimoto's thyroiditis (thyroid EMZL).
●Diagnosis – The diagnosis of EMZL is made based upon morphologic, immunophenotypic, and genetic analysis of biopsy material taken from an affected site, interpreted within the clinical context. Morphologic review reveals a polymorphous infiltrate of small cells with reactive follicles. While large cells are typically present, they are by definition in the minority. On immunophenotype, cells are positive for B cell markers CD19, CD20, and CD22, and negative for CD5, CD10, and CD23. Chromosomal abnormalities, usually trisomy 3 or t(11;18), are found in most cases.
●Differential diagnosis – The differential diagnosis of patients with EMZL includes reactive lesions, nodal and splenic marginal zone lymphoma, and other B cell lymphomas, most commonly diffuse large B cell lymphoma, small lymphocytic lymphoma, mantle cell lymphoma, and follicular lymphoma.
`;

interface GeneratorFormProps {
  onGenerate: (params: any) => void;
  isLoading: boolean;
  userRole?: UserRole;
}

const GeneratorForm: React.FC<GeneratorFormProps> = ({ onGenerate, isLoading, userRole }) => {
  const [contentType, setContentType] = useState('MCQ');
  const [generatorModel, setGeneratorModel] = useState('');
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [inputText, setInputText] = useState('');
  const [numQuestions, setNumQuestions] = useState(1);
  const [focusAreas, setFocusAreas] = useState('');
  // Separate temperature and top-p for generator and formatter
  const [generatorTemperature, setGeneratorTemperature] = useState(0.51);
  const [generatorTopP, setGeneratorTopP] = useState(0.95);
  const [formatterTemperature, setFormatterTemperature] = useState(0.51);
  const [formatterTopP, setFormatterTopP] = useState(0.95);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);
  const [isSavingPrompts, setIsSavingPrompts] = useState(false);
  const [promptsSaveStatus, setPromptsSaveStatus] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({ show: false, message: '', type: 'success' });
  
  // All 6 prompts state (MCQ, NMCQ, and Summary)
  const [mcqGeneratorPrompt, setMcqGeneratorPrompt] = useState('');
  const [mcqFormatterPrompt, setMcqFormatterPrompt] = useState('');
  const [nmcqGeneratorPrompt, setNmcqGeneratorPrompt] = useState('');
  const [nmcqFormatterPrompt, setNmcqFormatterPrompt] = useState('');
  const [summaryGeneratorPrompt, setSummaryGeneratorPrompt] = useState('');
  const [summaryFormatterPrompt, setSummaryFormatterPrompt] = useState('');
  
  // Original default prompts for reset functionality (never change these)
  const [originalDefaultPrompts, setOriginalDefaultPrompts] = useState({
    mcq_generator: '',
    mcq_formatter: '',
    nmcq_generator: '',
    nmcq_formatter: '',
    summary_generator: '',
    summary_formatter: ''
  });

  // Fetch available models on component mount
  useEffect(() => {
    const fetchModels = async () => {
      setModelsLoading(true);
      const response = await modelService.getAvailableModels();
      if (response && response.models) {
        setAvailableModels(response.models);
        // Set default model if available
        if (response.models.length > 0 && !generatorModel) {
          setGeneratorModel(response.models[0].name);
        }
      }
      setModelsLoading(false);
    };
    fetchModels();
  }, [userRole]);

  // Fetch prompts on component mount (admin only)
  useEffect(() => {
    if (userRole === 'admin') {
      const fetchPrompts = async () => {
        // Fetch current prompts (may be modified)
        const currentPrompts = await generationService.getCurrentPrompts();
        if (currentPrompts) {
          setMcqGeneratorPrompt(currentPrompts.mcq_generator);
          setMcqFormatterPrompt(currentPrompts.mcq_formatter);
          setNmcqGeneratorPrompt(currentPrompts.nmcq_generator);
          setNmcqFormatterPrompt(currentPrompts.nmcq_formatter);
          setSummaryGeneratorPrompt(currentPrompts.summary_generator || '');
          setSummaryFormatterPrompt(currentPrompts.summary_formatter || '');
        }
        
        // Fetch original default prompts for reset functionality
        const defaultPrompts = await generationService.getDefaultPrompts();
        if (defaultPrompts) {
          setOriginalDefaultPrompts(defaultPrompts);
        }
      };
      fetchPrompts();
    }
  }, [userRole]);

  // Hide save status after 3 seconds
  useEffect(() => {
    if (promptsSaveStatus.show) {
      const timer = setTimeout(() => {
        setPromptsSaveStatus({ show: false, message: '', type: 'success' });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [promptsSaveStatus.show]);

  const handleSavePrompts = async () => {
    if (!userRole || userRole !== 'admin') return false;
    
    setIsSavingPrompts(true);
    const promptsToSave = {
      mcq_generator: mcqGeneratorPrompt,
      mcq_formatter: mcqFormatterPrompt,
      nmcq_generator: nmcqGeneratorPrompt,
      nmcq_formatter: nmcqFormatterPrompt,
      summary_generator: summaryGeneratorPrompt,
      summary_formatter: summaryFormatterPrompt
    };
    
    const result = await generationService.savePrompts(promptsToSave);
    
    if (result.success) {
      setPromptsSaveStatus({ show: true, message: result.message || 'Prompts saved successfully!', type: 'success' });
      // Note: We don't update originalDefaultPrompts here - they should always remain the original defaults
    } else {
      setPromptsSaveStatus({ show: true, message: result.message || 'Failed to save prompts', type: 'error' });
    }
    
    setIsSavingPrompts(false);
    return result.success;
  };

  const handleSubmit = () => {
    if (!inputText.trim()) {
      alert('Please enter some text to analyze');
      return;
    }

    if (inputText.length < 50) {
      alert('Input text is too short. Please provide more content.');
      return;
    }

    if (!generatorModel) {
      alert('Please select a model');
      return;
    }

    if (availableModels.length === 0) {
      alert('No models are available. Please contact your administrator.');
      return;
    }

    const params: any = {
      content_type: contentType,
      generator_model: generatorModel,
      input_text: inputText,
      num_questions: numQuestions,
      focus_areas: focusAreas || null,
    };

    // Only include advanced settings if user is admin
    // Note: We no longer send custom prompts since they're saved on the backend
    if (userRole === 'admin') {
      params.generator_temperature = generatorTemperature;
      params.generator_top_p = generatorTopP;
      params.formatter_temperature = formatterTemperature;
      params.formatter_top_p = formatterTopP;
    } else {
      // Use default values for non-admin users
      params.generator_temperature = 0.51;
      params.generator_top_p = 0.95;
      params.formatter_temperature = 0.51;
      params.formatter_top_p = 0.95;
    }

    onGenerate(params);
  };

  const handleLoadSample = () => {
    setInputText(SAMPLE_INPUT);
  };

  const handleClear = () => {
    if (inputText && !confirm('Are you sure you want to clear the input?')) {
      return;
    }
    setInputText('');
    setFocusAreas('');
    // Note: We don't reset prompts anymore since they're saved on the backend
  };

  const charCount = inputText.length;
  const charCountColor = charCount > 140000 ? 'text-error' : 
                         charCount > 120000 ? 'text-warning' : 
                         'text-secondary';

  return (
    <>
      <div className="config-panel elegant-panel">
        <div className="panel-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"/>
          </svg>
        </div>
        <h2>Configuration</h2>
        
        <div className="config-grid">
          <div className="config-group">
            <label>Content Type</label>
            <div className="toggle-group">
              <input
                type="radio"
                id="mcq"
                name="contentType"
                value="MCQ"
                checked={contentType === 'MCQ'}
                onChange={(e) => setContentType(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="mcq" className="toggle-label">MCQ</label>
              
              <input
                type="radio"
                id="nmcq"
                name="contentType"
                value="NMCQ"
                checked={contentType === 'NMCQ'}
                onChange={(e) => setContentType(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="nmcq" className="toggle-label">Non-MCQ</label>
              
              <input
                type="radio"
                id="summary"
                name="contentType"
                value="SUMMARY"
                checked={contentType === 'SUMMARY'}
                onChange={(e) => setContentType(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="summary" className="toggle-label">Summary Bytes</label>
            </div>
            <small>MCQ: Multiple Choice | Non-MCQ: Clinical Vignettes | Summary: Clinical Summaries</small>
          </div>

          <div className="config-group">
            <label htmlFor="generatorModel">Generator Model</label>
            {modelsLoading ? (
              <div className="loading-models">Loading available models...</div>
            ) : availableModels.length === 0 ? (
              <div className="no-models-warning">
                ⚠️ No models available. Please contact your administrator.
              </div>
            ) : (
              <>
                <select
                  id="generatorModel"
                  value={generatorModel}
                  onChange={(e) => setGeneratorModel(e.target.value)}
                  disabled={isLoading || modelsLoading}
                  className="model-select"
                >
                  {availableModels.length === 1 ? (
                    // If only one model is available, show it directly without optgroup
                    <option value={availableModels[0].name}>
                      {availableModels[0].display_name || availableModels[0].name}
                    </option>
                  ) : (
                    // Group models by category if multiple are available
                    (() => {
                      const modelsByCategory = availableModels.reduce((acc, model) => {
                        if (!acc[model.category]) {
                          acc[model.category] = [];
                        }
                        acc[model.category].push(model);
                        return acc;
                      }, {} as Record<string, ModelInfo[]>);
                      
                      return Object.entries(modelsByCategory).map(([category, models]) => (
                        <optgroup key={category} label={category}>
                          {models.map(model => (
                            <option key={model.name} value={model.name}>
                              {model.display_name || model.name}
                            </option>
                          ))}
                        </optgroup>
                      ));
                    })()
                  )}
                </select>
                <small>
                  {availableModels.length === 1 
                    ? 'Only one model is available for your account'
                    : 'Select the AI model for content generation'
                  }
                </small>
              </>
            )}
          </div>

          <div className="config-group">
            <label htmlFor="numQuestions">Number of Questions</label>
            <input
              type="number"
              id="numQuestions"
              min="1"
              max="10"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              disabled={isLoading}
            />
            <small>Generate 1-10 questions</small>
          </div>

          <div className="config-group">
            <label htmlFor="focusAreas">Focus Areas (Optional)</label>
            <input
              type="text"
              id="focusAreas"
              placeholder="e.g., diagnosis, treatment, pathophysiology"
              value={focusAreas}
              onChange={(e) => setFocusAreas(e.target.value)}
              disabled={isLoading}
            />
            <small>Specific topics to emphasize</small>
          </div>

        </div>
        
        {userRole === 'admin' && (
        <div className="advanced-toggle" onClick={() => setShowAdvanced(!showAdvanced)}>
          <span className="toggle-text">
            {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
          </span>
          <svg 
            className={`toggle-arrow ${showAdvanced ? 'rotated' : ''}`}
            width="20" height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        )}

        {userRole === 'admin' && showAdvanced && (
        <div className="advanced-settings">
          <div className="settings-section">
            <h3>🤖 Generator Settings</h3>
            <div className="settings-grid">
              <div className="config-group">
                <label htmlFor="generator-temperature">
                  <span className="label-icon">🌡️</span>
                  Generator Temperature
                </label>
                <div className="slider-container">
                  <input
                    type="range"
                    id="generator-temperature"
                    min="0"
                    max="1"
                    step="0.01"
                    value={generatorTemperature}
                    onChange={(e) => setGeneratorTemperature(parseFloat(e.target.value))}
                    disabled={isLoading}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={generatorTemperature}
                    onChange={(e) => setGeneratorTemperature(parseFloat(e.target.value))}
                    disabled={isLoading}
                    className="slider-value"
                  />
                </div>
                <small>Controls randomness in generation (0 = focused, 1 = creative)</small>
              </div>

              <div className="config-group">
                <label htmlFor="generator-topP">
                  <span className="label-icon">🎯</span>
                  Generator Top-P
                </label>
                <div className="slider-container">
                  <input
                    type="range"
                    id="generator-topP"
                    min="0"
                    max="1"
                    step="0.01"
                    value={generatorTopP}
                    onChange={(e) => setGeneratorTopP(parseFloat(e.target.value))}
                    disabled={isLoading}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={generatorTopP}
                    onChange={(e) => setGeneratorTopP(parseFloat(e.target.value))}
                    disabled={isLoading}
                    className="slider-value"
                  />
                </div>
                <small>Nucleus sampling for generation</small>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>📝 Formatter Settings</h3>
            <div className="settings-grid">
              <div className="config-group">
                <label htmlFor="formatter-temperature">
                  <span className="label-icon">🌡️</span>
                  Formatter Temperature
                </label>
                <div className="slider-container">
                  <input
                    type="range"
                    id="formatter-temperature"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formatterTemperature}
                    onChange={(e) => setFormatterTemperature(parseFloat(e.target.value))}
                    disabled={isLoading}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formatterTemperature}
                    onChange={(e) => setFormatterTemperature(parseFloat(e.target.value))}
                    disabled={isLoading}
                    className="slider-value"
                  />
                </div>
                <small>Controls randomness in formatting (0 = consistent, 1 = varied)</small>
              </div>

              <div className="config-group">
                <label htmlFor="formatter-topP">
                  <span className="label-icon">🎯</span>
                  Formatter Top-P
                </label>
                <div className="slider-container">
                  <input
                    type="range"
                    id="formatter-topP"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formatterTopP}
                    onChange={(e) => setFormatterTopP(parseFloat(e.target.value))}
                    disabled={isLoading}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formatterTopP}
                    onChange={(e) => setFormatterTopP(parseFloat(e.target.value))}
                    disabled={isLoading}
                    className="slider-value"
                  />
                </div>
                <small>Nucleus sampling for formatting</small>
              </div>
            </div>
          </div>
        </div>
        )}
      </div>

      {userRole === 'admin' && (
      <div className="prompts-panel elegant-panel">
        <div className="prompts-header" onClick={() => setShowPrompts(!showPrompts)}>
          <div className="header-left">
            <div className="panel-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <h2>Prompt Templates</h2>
            <span className="prompt-subtitle">(Click to view and edit all 6 prompts)</span>
          </div>
          <svg 
            className={`toggle-arrow ${showPrompts ? 'rotated' : ''}`}
            width="20" height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        
        {showPrompts && (
          <div className="all-prompts-container">
            <div className="prompts-grid">
              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>📝 MCQ Generator Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setMcqGeneratorPrompt(originalDefaultPrompts.mcq_generator)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={mcqGeneratorPrompt}
                  onChange={(e) => setMcqGeneratorPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for generating MCQ questions</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>🎨 MCQ Formatter Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setMcqFormatterPrompt(originalDefaultPrompts.mcq_formatter)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={mcqFormatterPrompt}
                  onChange={(e) => setMcqFormatterPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for formatting MCQ output</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>📋 Non-MCQ Generator Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setNmcqGeneratorPrompt(originalDefaultPrompts.nmcq_generator)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={nmcqGeneratorPrompt}
                  onChange={(e) => setNmcqGeneratorPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for generating Non-MCQ questions</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>🖌️ Non-MCQ Formatter Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setNmcqFormatterPrompt(originalDefaultPrompts.nmcq_formatter)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={nmcqFormatterPrompt}
                  onChange={(e) => setNmcqFormatterPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for formatting Non-MCQ output</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>📊 Summary Bytes Generator Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setSummaryGeneratorPrompt(originalDefaultPrompts.summary_generator)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={summaryGeneratorPrompt}
                  onChange={(e) => setSummaryGeneratorPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for generating Summary Bytes</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>✏️ Summary Bytes Formatter Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setSummaryFormatterPrompt(originalDefaultPrompts.summary_formatter)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={summaryFormatterPrompt}
                  onChange={(e) => setSummaryFormatterPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for formatting Summary Bytes output</small>
              </div>
            </div>
            
            <div className="prompts-footer">
              {promptsSaveStatus.show && (
                <div className={`save-status ${promptsSaveStatus.type}`}>
                  {promptsSaveStatus.message}
                </div>
              )}
              <div className="prompt-actions" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <button 
                  className="btn btn-outline"
                  onClick={async () => {
                    // First reset on backend
                    const result = await generationService.resetPromptsToDefaults();
                    if (result.success) {
                      // Then update UI with original defaults
                      setMcqGeneratorPrompt(originalDefaultPrompts.mcq_generator);
                      setMcqFormatterPrompt(originalDefaultPrompts.mcq_formatter);
                      setNmcqGeneratorPrompt(originalDefaultPrompts.nmcq_generator);
                      setNmcqFormatterPrompt(originalDefaultPrompts.nmcq_formatter);
                      setSummaryGeneratorPrompt(originalDefaultPrompts.summary_generator);
                      setSummaryFormatterPrompt(originalDefaultPrompts.summary_formatter);
                      setPromptsSaveStatus({ 
                        show: true, 
                        message: result.message || 'Prompts reset to defaults successfully!', 
                        type: 'success' 
                      });
                    } else {
                      setPromptsSaveStatus({ 
                        show: true, 
                        message: result.message || 'Failed to reset prompts', 
                        type: 'error' 
                      });
                    }
                  }}
                  disabled={isLoading || isSavingPrompts}
                >
                  Reset All to Defaults
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={async () => {
                    if (confirm('This will update the default prompts with your current prompts. Are you sure?')) {
                      setIsSavingPrompts(true);
                      // First save current prompts
                      await handleSavePrompts();
                      
                      // Then update defaults
                      const result = await generationService.updateDefaultPrompts();
                      if (result.success) {
                        // Update the original defaults in state
                        setOriginalDefaultPrompts({
                          mcq_generator: mcqGeneratorPrompt,
                          mcq_formatter: mcqFormatterPrompt,
                          nmcq_generator: nmcqGeneratorPrompt,
                          nmcq_formatter: nmcqFormatterPrompt,
                          summary_generator: summaryGeneratorPrompt,
                          summary_formatter: summaryFormatterPrompt
                        });
                        setPromptsSaveStatus({ 
                          show: true, 
                          message: 'Default prompts updated successfully!', 
                          type: 'success' 
                        });
                      } else {
                        setPromptsSaveStatus({ 
                          show: true, 
                          message: result.message || 'Failed to update default prompts', 
                          type: 'error' 
                        });
                      }
                      setIsSavingPrompts(false);
                    }
                  }}
                  disabled={isLoading || isSavingPrompts}
                  title="Save current prompts as the new defaults"
                >
                  {isSavingPrompts ? 'Updating...' : 'Save as New Defaults'}
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={handleSavePrompts}
                  disabled={isLoading || isSavingPrompts}
                >
                  {isSavingPrompts ? 'Saving...' : 'Save All Prompts'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      )}

      <div className="input-panel elegant-panel">
        <div className="panel-header">
          <div className="panel-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <h2>Input Text</h2>
          <div className={`char-counter ${charCountColor}`}>
            <span>{charCount.toLocaleString()}</span> / 500,000 characters
          </div>
        </div>
        
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste or type your educational content here..."
          maxLength={500000}
          disabled={isLoading}
        />
        
        <div className="action-buttons">
          <button 
            onClick={handleClear} 
            className="btn btn-outline"
            disabled={isLoading}
          >
            Clear
          </button>
          <button 
            onClick={handleLoadSample} 
            className="btn btn-outline"
            disabled={isLoading}
          >
            Load Sample
          </button>
          <button 
            onClick={handleSubmit} 
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span>Generating...</span>
                <span className="spinner"></span>
              </>
            ) : (
              'Generate Content'
            )}
          </button>
        </div>
      </div>
    </>
  );
};

export default GeneratorForm;
