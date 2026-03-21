# Prompt Index
## SCE Color Replication Study

Each prompt is stored as a plain text file. The harness reads the file and inserts it as the user message alongside the stimulus image.

No system prompt is used. Raw model behavior only.

---

## Prompt Files

| ID | File | Type | Used With | Purpose |
|---|---|---|---|---|
| P01 | P01_describe_vehicles.txt | Narrative | S001, S002, S003 | Open-ended color description of both vehicles |
| P02 | P02_measure_vehicles.txt | Analytical | S001, S002, S003 | Request hue measurement in degrees |
| P03 | P03_describe_fruit.txt | Narrative | S004, S005, S006 | Open-ended color description of single food item |
| P04 | P04_measure_fruit.txt | Analytical | S004, S005, S006 | Request hue measurement in degrees |
| P05 | P05_describe_scene.txt | Narrative | S007 | Open-ended color description of cube and fence |
| P06 | P06_measure_scene.txt | Analytical | S007 | Request hue measurement in degrees |

## Condition-to-Prompt Mapping

| Condition | Stimulus | Prompt |
|---|---|---|
| C01 | S001 | P01 |
| C02 | S001 | P02 |
| C03 | S002 | P01 |
| C04 | S002 | P02 |
| C05 | S003 | P01 |
| C06 | S003 | P02 |
| C07 | S004 | P03 |
| C08 | S004 | P04 |
| C09 | S005 | P03 |
| C10 | S005 | P04 |
| C11 | S006 | P03 |
| C12 | S006 | P04 |
