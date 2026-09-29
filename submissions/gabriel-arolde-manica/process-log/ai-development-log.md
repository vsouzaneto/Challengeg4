# AI Development Process Log

## 1. Problem framing

I used AI to help break down the business problem into a practical product requirement:

> How can a sales representative quickly identify which open opportunities deserve attention and understand why?

The initial approach considered building a predictive model, but the challenge emphasized usefulness, explainability and a 
limited development time. This led to an explainable priority-scoring approach.

## 2. Data exploration

AI was used to help identify potentially useful features in the CRM dataset.

The analysis examined:

* deal stage;
* time in pipeline;
* product;
* account revenue;
* employees;
* sales representative;
* regional office;
* historical Won/Lost outcomes.

The data showed that stage and pipeline age were more directly actionable than some other available features.

Historical product win rates were relatively close together, so product was treated as a secondary signal rather than the main 
driver of the score.

## 3. First scoring approach

The first scoring version combined:

* deal stage;
* time in Engaging;
* historical product win rate;
* account revenue;
* account data availability.

The first implementation was tested against all 2,089 open opportunities.

## 4. Human validation and iteration

The first test revealed an important issue:

20 of the highest-ranked opportunities received the maximum score of 100.

This indicated that the initial scoring system produced too many ties at the top and was not granular enough for a real seller 
prioritization workflow.

Instead of accepting the first AI-generated approach, the scoring logic was reviewed against the actual dataset.

The time component was then made more granular:

* up to 30 days;
* 31–90 days;
* 91–180 days;
* 181–270 days;
* more than 270 days.

The revised version also treats very old opportunities as potential pipeline-stagnation risks.

## 5. Product implementation

AI was used to assist with implementation of:

* Python scoring functions;
* Pandas data processing;
* Streamlit dashboard;
* Plotly visualizations;
* filtering;
* opportunity ranking;
* score explanations.

The implementation was executed and tested locally against the real dataset.

## 6. Final solution

The final solution is a Streamlit application called **DealPilot**.

The application provides:

* open pipeline overview;
* Priority Score from 0–100;
* seller filters;
* manager filters;
* regional filters;
* stage filters;
* top-priority opportunities;
* explanations for each score;
* risk flags.

The score is explicitly presented as a **commercial priority score**, not a probability of winning.

## 7. Key lesson

The main role of AI in this project was not simply generating code.

AI was used as a development partner for:

1. problem decomposition;
2. hypothesis generation;
3. implementation;
4. testing;
5. critique;
6. iteration;
7. documentation.

The final logic was validated against the dataset and modified after observing real test results.

