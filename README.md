# AI Scientific Index

This repository builds the backbone for an **AI Scientific Index**: a [Clio](https://www.anthropic.com/research/clio$0)-based taxonomy and dataset that allows us to study empirically how people use AI for scientific research, in the same spirit as Anthropic’s work on:

* the [**Economic Index**](https://www.anthropic.com/news/the-anthropic-economic-index$0) (O*NET tasks),
* [**Moral Values**](https://www.anthropic.com/research/values-wild$0) in the wild,
* **Education** for [students](https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude$0) and [educators](https://www.anthropic.com/news/anthropic-education-report-how-educators-use-claude$0).

In each of these frameworks, a societal domain (the economy, morality, education) is paired with a structured taxonomy that spans the breadth of human activity within that domain, and Claude conversations are classified against that taxonomy to understand real-world impact.

Here, the domain is **scientific research**, and our taxonomy is built from the **National Science Foundation (NSF) award database**, which categorizes each award within a domain-based hierarchy (directorates → divisions → programs), with dollars awarded over time as an attached signal of societal investment.

By creating a comprehensive taxonomy of scientific domains from the NSF awards database, we can apply Anthropic's Clio methodology to map and measure the impact of AI on the scientific landscape on the basis of an existing language of science.

The goal is to move beyond speculation and create a data-driven view of where AI is acting as a catalyst, which fields are being transformed, and how researchers are leveraging AI on the ground, from automating data analysis to generating novel hypotheses. This allows us to track emerging habits, identify risks, and align the development of AI with societal benefit.

This repository handles the taxonomy curation portion of the analysis, including:

* Parsing NSF award JSONs by year.
* Normalizing directorates, divisions, programs, and program codes.
* Aggregating awards into a nested research hierarchy.
* Exporting a clean taxonomy suitable for Clio classification.
* Providing award-level CSVs, funding time series, and division mission statements.
* Offering basic visualizations of funding by division and directorate.

The Clio methodology, which classifies Claude conversations into this taxonomy and computes metrics like AI usage per program, sits on top of this foundation.

## Motivations & Societal Impact: Why Science and Why Now?

In his seminal 1945 report *Science, The Endless Frontier*, Vannevar Bush argues that basic research -- the pure, curiosity-driven exploration of the unknown -- is the "pacemaker of technological progress." He posits that while industry is well-suited to commercialize existing knowledge, it cannot be expected to fund the foundational, high-risk research whose practical benefits may require decades to materialize. This funding, he claims, is a fundamental responsibility of a central institution that could allocate value to the vast expanses of human inquiry. The NSF is the direct result of this vision: an institution designed to fill the reservoir of human knowledge from which all downstream innovations are drawn, and consequently, it has given us an extremely rich, 66-year dataset of the wide range of exploratory scientific domains researchers target in their work.

AI, in many ways, resembles Bush's hypothesized *memex* -- a device that could contain all knowledge and be summoned to produce it at the whim of its user. And for the first time in history, technology like Clio allows us to understand what the aggregate of human minds *wonder* across all of the world's individual memexes in pursuit of that *pure, curiosity-driven exploration of the unknown* so foundational to basic research.

The NSF awards database is consequently more than just a list of grants; when paired with real AI usage, it is the most structured and comprehensive record of this "endless frontier." It is the perfect taxonomy to serve as the bedrock for analyzing the impact of AI on science.

The leading AI labs center much their optimism toward AI advancement around the rise of autonomous and highly augmented scientific research, and rightfully so -- the promise of exponentially frequent scientific discoveries has countless downstream implications on human welfare. Hundreds of billions of dollars in capital are being invested on the basis of this thesis of "automated science," where the horizons of knowledge are no longer limited by the speed or constraints of human thought. And yet we have no formal idea of how AI is being applied to scientific research writ large. The AI Scientific Index is designed to measure whether what that might look like.

Here is a subset of sample empirical questions we would be able to answer with this approach:

1. Which scientific fields are being impacted first and most profoundly by AI? Is AI accelerating progress evenly, or are there specific domains, like materials science or genomics, that are pulling ahead?
2. Are scientists primarily using AI as a sophisticated calculator for data analysis, or as a creative partner for generating novel ideas? The `Research Mode` and `Research Action` facets provide a direct lens into this.
3. How does scientific inquiry map to funding? The results can provide invaluable feedback to funding bodies like the NSF. By seeing where AI is having the greatest impact, they can strategically invest in programs and education to amplify these benefits, or they can choose to invest in weakly present domains.
4. Does AI's training data cause it to favor certain research paths over others? Are there fields where AI-generated information is less reliable? This framework provides an early warning system to detect and mitigate such risks.


## Methodology
While the NSF awards database is, at its heart, a list of several hundred thousand grants issued over six decades, it's also a hierarchical encoding of scientific inquiry as American institutions would classify them.

* **Directorate** → e.g., a broad area of science.
* **Division** → more specific sub-domain.
* **Program / Program Element** → a concrete programmatic focus, with its own code, scope, and budget.

Each award JSON contains:

* organizational metadata (`org_dir_long_name`, `org_div_long_name`, abbreviations),
* one or more **program elements** (names + codes),
* **amounts awarded**, effective and expiration dates,
* PIs and institutions,
* additional funding & obligation fields.

That means we can treat this data as:

* a **taxonomy** (directorate → division → program), and
* a **time series of investment** into each node of that taxonomy, via yearly award amounts.

We turn this raw NSF data into a machine-readable hierarchy that can be fed as digestible classification options into Clio in order to replicate the sort of analytical foundation we're looking for with the following steps:

1.  **Data Ingestion**: The pipeline downloads and processes annual award data archives directly from the NSF, covering a multi-decade span. **NOTE:** The NSF recently changed its programmatic data access protocol, and it is no longer possible to scrape all the award years at once. The next best path is to download ZIP files for each year from [this](https://www.nsf.gov/awardsearch/download-awards/) page and place them into /data/awards. Downloading these ZIP files is by far the easiest and quickest way to get the full award dataset.
2.  **Parsing & Structuring**: Each individual award is parsed from its raw format. Key information (including the funding amount, year, and its classification within the NSF's organizational hierarchy) is extracted.
3.  **Hierarchical Aggregation**: The individual awards are aggregated into a comprehensive, three-level hierarchy: *Directorate → Division → Program*. Funding amounts and award counts are summed at each level, both in aggregate and for each year.
4.  **Taxonomy Generation**: The final, structured hierarchy is exported into two formats for analysis:
    *   `outputs/taxonomy.json`: A nested JSON object representing the full hierarchy of scientific domains.
    *   `outputs/taxonomy.tsv`: A flat, three-column file ideal for use in iterative classification tasks. **This is the primary input dataset for Clio.**
5. **Other Outputs**: We also output the following files:
   * award-level CSV (`outputs/awards.csv`): a single file containing all the data.
   * nested research hierarchy (`outputs/research.json`): granular funding and award amounts per program per year.
   * a compact “brief” hierarchy (`outputs/research_brief.json`): funding and award amounts aggregated at the program level across all years.


Here is a sample of the taxonomy:

```text
"Directorate for Geosciences": {
    "Division of Atmospheric and Geospace Sciences": [
      "Climate & Large-Scale Dynamics",
      "Physical & Dynamic Meteorology",
      "Atmospheric Chemistry",
      "AERONOMY",
      "SOLAR-TERRESTRIAL"
    ],
    "Division Of Ocean Sciences": [
      "SHIP OPERATIONS",
      "OCEAN DRILLING PROGRAM",
      "BIOLOGICAL OCEANOGRAPHY",
      "PHYSICAL OCEANOGRAPHY",
      "Marine Geology and Geophysics",
      "Chemical Oceanography"
    ]
}
```

## Prompts for a Clio-based Analysis

To analyze how users are leveraging AI for scientific work, we can apply a series of prompts to classify conversations against our new taxonomy.

### 1. Screener Prompt

This initial prompt filters for relevant conversations.

```markdown
Human: The following is a conversation between an AI assistant and a user:
{conversation}
Assistant: I understand.

Human: Your job is to answer this question about the preceding conversation:
<question>
Does this conversation relate to scientific research, experimentation, data analysis, or the exploration of technical concepts? Answer either "Yes" or "No" with no other commentary.
</question>

What is the answer? You MUST answer either only "Yes" or "No". Provide the answer in <answer> tags with no other commentary.
     
Assistant: Sure, the answer to the question is: <answer>
```

### 2. Classification Prompt (Iterative)

This prompt maps a conversation to the most relevant domain within the NSF taxonomy. It is applied iteratively, first for Directorates, then Divisions, then Programs.

```markdown
Human: The following is a scientific or technical discussion between an AI assistant and a user:

{conversation}

Assistant: I understand.

Human: The following is a list of scientific domains funded by the National Science Foundation. Your job is to identify which domain best describes the scope of the conversation. Consider all the options before you answer.

{options_str}

What is the answer? You MUST provide an option exactly as written above. If multiple options apply, choose the single-most pertinent one. Do not return an answer except one of the options presented above. First, start off by considering various aspects of the technical discussion in <scratchpad> tags in at most four sentences, and then provide the final, exact answer in <answer> tags with no other commentary.
```

### 3. Facet: Research Mode

This facet determines the user's approach to using the AI.

```markdown
Human: You are an expert in the scientific research process. Your job is to classify how the user is interacting with the AI assistant based on the following modes:

- "AUTONOMOUS_TASK": The user is instructing the AI to perform a specific, well-defined task on its own (e.g., "Analyze this data and plot the results," "Write Python code to simulate this process").
- "COLLABORATIVE_PARTNER": The user is engaging the AI in a creative or exploratory dialogue (e.g., "What are some novel hypotheses to explain this phenomenon?," "Let's brainstorm potential experimental designs").
- "EDUCATIONAL_TOOL": The user is asking the AI to explain, summarize, or teach a scientific concept (e.g., "Explain how CRISPR-Cas9 works," "What's the difference between a T-test and an ANOVA?").

Which mode best describes the user's interaction? You MUST provide one of the three options exactly as written above.

Assistant: Sure, the answer to the question is: <answer>
```

### 4. Facet: Research Action

This facet identifies the specific research activity being performed, based on common use cases.

```markdown
Human: Your job is to identify the primary research activity the user is performing with the AI assistant from the list below:

- "LITERATURE_REVIEW": Synthesizing papers, finding citations, summarizing existing research.
- "DATA_ANALYSIS": Processing, interpreting, or visualizing numerical data.
- "HYPOTHESIS_GENERATION": Creating new, testable ideas or research questions.
- "EXPERIMENTAL_DESIGN": Outlining protocols, methods, or experimental steps.
- "CODE_GENERATION": Writing or debugging code for analysis, simulation, or modeling.
- "WRITING_SUPPORT": Drafting, editing, or refining research papers, grants, or reports.

Which action best describes the conversation? You MUST provide one of the options exactly as written above.

Assistant: Sure, the answer to the question is: <answer>
```

## Running the Pipeline

Recall: Downloading [these](https://www.nsf.gov/awardsearch/download-awards/) ZIP files is by far the easiest and quickest way to get the full award dataset.
After downloading them and placing the files into `data/awards/`, run the following command to kick off the process:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the full pipeline from 1960-2025
python3 main.py 1960 2025 --skip-download
```

That's it! You'll find your taxonomy files and the adjacent outputs in `outputs/`.

You can selectively skip other stages, as well if you're looking to finetune something:

```bash
# Reuse previously downloaded & extracted data, just re-parse and re-aggregate
python3 main.py 1960 2025 --skip-download --skip-extract

# Only rebuild taxonomy and visualizations from an existing research.json
python3 main.py 1960 2025 --skip-download --skip-extract --skip-parse --skip-mappings --skip-aggregate
```

Key flags:

* `--skip-download`
* `--skip-extract`
* `--skip-parse`
* `--skip-mappings`
* `--skip-aggregate`
* `--skip-taxonomy`
* `--skip-visualize`
* `--skip-missionscrape`
* `--skip-export`
* `--year-sort YEAR` to write `research_YEAR.json` sorted by that year’s funding.

## Repository Layout

```text
.
├── data/
│   └── awards/                 # Raw NSF award JSONs, organized by year (created by the pipeline)
├── nsf_award_downloads/        # Optional / legacy scratch space
├── nsf_awards/                 # Optional / legacy scratch space
├── outputs/
│   ├── research.json           # Full nested hierarchy with metrics
│   ├── research_brief.json     # Compact summary per directorate/division/program
│   ├── research_YYYY.json      # Optional hierarchy sorted by a specific year
│   ├── taxonomy.json           # directorate → division → [program] tree for classification
│   ├── taxonomy.tsv            # Flat taxonomy table: directorate, division, program
│   ├── awards.csv              # Flattened award-level dataset
│   ├── directorate_map.json    # long_name → abbr
│   ├── division_map.json       # long_name → {abbr, mission?}
│   ├── program_map.json        # program_name → code
│   ├── division_urls.txt       # NSF URLs used to scrape mission statements
│   └── ...                     # Any visualizations or additional artifacts
├── prompts/
|   ├── classification.md       # Hierarchy mapping
│   ├── research_action.md      # Task being done by user
│   ├── research_mode.md        # Research category
│   └── screener.md             # Whether to include user conversation
├── src/
│   ├── downloader.py           # Download NSF award ZIPs by year
│   ├── extractor.py            # Unzip award archives into data/awards/{year}/
│   ├── parser.py               # Parse JSON awards into flat records
│   ├── mappings.py             # Build directorate/division/program maps + division URLs
│   ├── aggregator.py           # Aggregate records into the research hierarchy
│   ├── taxonomy.py             # Generate taxonomy.json / taxonomy.tsv from the hierarchy
│   ├── visualize.py            # Basic funding visualizations using research.json
│   ├── mission_scraper.py      # Scrape division mission statements and enrich division_map.json
│   └── export_awards.py        # Flatten awards into outputs/awards.csv
├── main.py                     # Orchestrator for the end-to-end pipeline
├── README.md                   # README.md
└── requirements.txt            # Python dependencies
```

## Appendix

### 1. Parsing Details

`src/parser.py` traverses `data/awards` and parses each JSON file via `parse_award`:

Each parsed record includes (when present):

* `year` (inferred from folder name),
* `dir_abbr`, `directorate`,
* `div_abbr`, `division`,
* `program`, `pgm_code`,
* `amount` (award amount).

All records are returned as a flat list:

```python
records = parse_all(DATA_DIR, max_workers=MAX_PARSE_WORKERS)
```

### 2. Building maps & URLs

`src/mappings.py:build_maps(records, output_dir)` constructs:

* `directorate_map.json` → `{ long_name: abbr }`
* `division_map.json`    → `{ long_name: abbr }` (later enriched with missions)
* `program_map.json`     → `{ program_name: code }`
* `division_urls.txt`    → `https://www.nsf.gov/{dir_abbr}/{div_abbr}` per valid pair

Special handling ensures:

* messy abbreviations like `"O/D"` become `"OD"`,
* self-equal `dir_abbr == div_abbr` combos are skipped,
* a curated set of **Office of the Director (OD)** combinations are injected so mission scraping works uniformly.

### 3. Award-level export

`src/export_awards.py` flattens each award into a **wide CSV**:

* One row per award file.
* Includes:

  * core identifiers (`awd_id`, dates, amounts),
  * directorate/division fields,
  * concatenated program elements and references,
  * PI names and roles,
  * institution information,
  * obligation year/amount series, etc.

Output: `outputs/awards.csv`.

This CSV is useful for:

* joining Clio-derived classification results back to **concrete awards and institutions**,
* building secondary datasets (e.g., by PI, institution, or state).

### 4. Aggregation into research hierarchies

`src/aggregator.py` (called in `main.py`) builds the nested `hierarchy`:

```python
hierarchy = build_hierarchy(records)
sorted_full    = sort_hierarchy(hierarchy)
brief_unsorted = {d: make_brief(sub) for d, sub in hierarchy.items()}
sorted_brief   = sort_hierarchy(brief_unsorted)
```

At each node (directorate, division, program), aggregator computes metrics like:

* `num_awards_total`, `num_awards_YEAR`
* `amt_awarded_total`, `amt_awarded_YEAR`

and returns a nested dict. That structure is:

* written as `outputs/research.json` (full hierarchy), and
* summarized into `outputs/research_brief.json` (fewer metrics, more compact).

Optionally, `sort_hierarchy_by_year` can sort nodes by a particular year’s funding:

```bash
python3 main.py 1990 2025 --year-sort 2020
# → outputs/research_2020.json
```

### 5. Taxonomy export

`src/taxonomy.py:generate_taxonomy` reads `research.json` and writes:

* `taxonomy.json` for hierarchical use,
* `taxonomy.tsv` for CSV/TSV-friendly workflows.

It explicitly **filters out all metrics** (`num_awards_*`, `amt_awarded_*`) so downstream Clio prompts only see **clean, human-readable labels**.

### 6. Visualization

`src/visualize.py` provides a small plotting utility using `pandas` and `matplotlib`:

* `plot_top_divisions(df)` → horizontal bar chart of top-10 divisions by total funding.
* `plot_directorate_timeseries(df)` → funding over time by directorate.

Run via:

```bash
python3 -m src.visualize --json outputs/research.json
```

or implicitly through `main.py` (unless `--skip-visualize` is set).

### 7. Mission statements

`src/mission_scraper.py` uses `division_urls.txt` to fetch mission statements from NSF pages and merges them into `division_map.json`.