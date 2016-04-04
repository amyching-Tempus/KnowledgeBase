 /*-------------------------------------------------------------------------*
 | Program:      Positive and Negative Control Betas                        |
 | Purpose:      Saves the betas generated from the model trying to tell    |
 |				 apart drugs that cause an HOI (positive controls) and      |
 |				 drugs that do not cause an HOI (negative controls).        |
 | Author(s):    Erica Voss                                                 |
 |                                                                          |
 | Version:      1.0                                                        |
 | Last revised: 09FEB016                                                   |
 *-------------------------------------------------------------------------*/

CREATE TABLE POSITIVE_NEGATIVE_CONTROL_BETAS (
	EVIDENCE_TYPE		VARCHAR(MAX),
	MODALITY			CHAR(1),
	BETA				FLOAT		
)

INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('intercept',NULL,-2.8754956511482)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('MEDLINE_MeSH_ClinTrial','T',0.00178826606757134)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('MEDLINE_MeSH_CR','T',1.53751512065998)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('MEDLINE_MeSH_Other','T',0.0124224840556044)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('MEDLINE_SemMedDB_ClinTrial','T',0.0392995392744758)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('MEDLINE_SemMedDB_CR','T',0.0468068992637764)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('SPL_EU_SPC','T',0.359059520480277)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('SPL_SPLICER_ADR','T',1.55866404312106)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('aers_report_count','T',0.382609789666565)
INSERT INTO POSITIVE_NEGATIVE_CONTROL_BETAS (EVIDENCE_TYPE, MODALITY, BETA) VALUES('aers_report_prr','T',0)


SELECT *
FROM POSITIVE_NEGATIVE_CONTROL_BETAS