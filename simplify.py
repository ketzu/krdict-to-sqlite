from collections import defaultdict
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
any_error = False

known_values = defaultdict(set)

def simplify(obj, path="root"):
    global any_error
    if isinstance(obj, list):
        return [simplify(item, path=f"{path}[{i}]") for i, item in enumerate(obj)]

    elif isinstance(obj, dict):
        new_obj = {}
        if "att" in obj and "val" in obj:
            att_key = obj["att"]
            val_val = obj["val"]
            if att_key in obj:
                logger.error(f"[ERROR] Key collision at {path}: key '{att_key}' already exists.")
                any_error = True
                # keep the original in this case
                new_obj["att"] = att_key
                new_obj["val"] = val_val
            else:
                new_obj[att_key] = val_val

        for k, v in obj.items():
            if k in ["att", "val"]:
                continue
            simplified_value = simplify(v, path=f"{path}.{k}")
            if (k == "feat" or k == "Lemma") and isinstance(simplified_value, list):
                sets_of_keys = [set(item.keys()) for item in simplified_value if isinstance(item, dict)]
                if len(sets_of_keys) > 0 and len(set.intersection(*sets_of_keys)) > 0:
                    continue
                merged_dict = {}
                for item in simplified_value:
                    if isinstance(item, dict):
                        for sub_k, sub_v in item.items():
                            if sub_k in merged_dict:
                                if isinstance(merged_dict[sub_k], list):
                                    merged_dict[sub_k].append(sub_v)
                                else:
                                    merged_dict[sub_k] = [merged_dict[sub_k], sub_v]
                            else:
                                merged_dict[sub_k] = sub_v
                simplified_value = merged_dict
                
                
            new_obj[k] = simplified_value

    
        if "feat" in new_obj and isinstance(new_obj["feat"], dict):
            if len(set(new_obj).intersection(set(new_obj["feat"].keys()))) == 0:
                for k, v in new_obj["feat"].items():
                    new_obj[k] = v
                del new_obj["feat"]

        for k,v in new_obj.items():
            if k not in ["sound", "label", "id", "url", "writtenForm", "variant", "lemma", "definition", "example", "syntacticPattern", "pronunciation", "example", "origin", "annotation"] and isinstance(v, str):
                known_values[k].add(v)
        return new_obj

    else:
        return obj


Path("simplified").mkdir(exist_ok=True)
for json_file in Path('data').glob("*.json"):
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
    simplified = simplify(data)
    with open(Path(f"simplified/{json_file.name}"), 'w', encoding="utf-8") as f_out:
        json.dump(simplified, f_out, ensure_ascii=False, indent=2)


if not any_error:
    logger.info("All JSON files simplified successfully.")


with open("known_values.json", "w", encoding="utf-8") as f:
    json.dump({k: list(v) for k, v in known_values.items()}, f, indent=2, ensure_ascii=False)
