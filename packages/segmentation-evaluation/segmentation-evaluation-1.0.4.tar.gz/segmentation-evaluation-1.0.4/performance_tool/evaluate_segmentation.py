"""
The package contains all the functions used to evaluate the segmentation
"""
import json
import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))
from performance_tool.performance_polygons import CorrectPolygon, ToEvaluatePolygon


def claster_on_label(data: dict, correct: bool) -> dict:
    """
    Given the dictionary with all the polygons serialized return another dictionary in which keys are the distinct
    labels of the input data.
    The value of each key is a list of polygon object. They are two different object depends on the input data collects
    the correct objects or objects to evaluate.

    :param data: The dictionary contains all polygons serialized
    :type data: dict
    :param correct: The value that represent if the input data are the correct polygons or polygons to check
    :type correct: bool
    :return: Polygons clustered on the label name. Dictionary with keys distinct labels
    :rtype: dict
    """
    polygons = {}
    for _, v in data.items():
        if correct:
            p = CorrectPolygon(v)
        else:
            p = ToEvaluatePolygon(v)

        l = v['label'].lower()

        if l not in polygons:
            polygons[l] = []

        polygons[l].append(p)

    return polygons


def evaluate_segmentation() -> bool:
    """
    The function ask for the two json file to match.

    The structure of the JSON must be a dictionary as key an increment number that represent uniquely an object.
    The value is another dictionary with two key *label* (the name of the template) and *points* (a list of float).

    :return: A bool value that check if all operations end correctly
    :rtype: bool
    """
    correct = False
    correct_segmentation_path = ''
    while not correct:
        correct_segmentation_path = input('Insert the path to the json file of the manually segmentation (ground '
                                          'truth):\n')
        if os.path.exists(correct_segmentation_path) and os.path.isfile(correct_segmentation_path):
            correct = True

    correct = False
    to_evaluate_segmentation_path = ''
    while not correct:
        to_evaluate_segmentation_path = input('Insert the path to the json file of the segmentation to evaluate:\n')
        if os.path.exists(to_evaluate_segmentation_path) and os.path.isfile(to_evaluate_segmentation_path):
            correct = True

    correct = False
    result_path = ''
    while not correct:
        result_path = input('Insert the path to the folder in which save the evaluation:\n')
        if os.path.exists(result_path) and os.path.isdir(result_path):
            correct = True

    with open(correct_segmentation_path) as json_file:
        data = json.load(json_file)

        correct_polygons = claster_on_label(data, correct=True)

    # print('CORRECT')
    # for k, v in correct_polygons.items():
    #     print(k, len(v))

    with open(to_evaluate_segmentation_path) as json_file:
        data = json.load(json_file)

        to_evaluate_polygons = claster_on_label(data, correct=False)

    # print('TO EVALUATE')
    # for k, v in to_evaluate_polygons.items():
    #     print(k, len(v))

    for k, p in to_evaluate_polygons.items():
        to_eval_pols_labeled = p

        if k in correct_polygons:
            correct_pols_labeled = correct_polygons[k].copy()
        else:
            correct_pols_labeled = []

        for pol in to_eval_pols_labeled:
            pol: ToEvaluatePolygon = pol
            iou, match = pol.find_best_iou(correct_pols_labeled)

            if iou > 0.8:
                correct_pols_labeled.remove(match)
                pol.match = match

    performance = {}

    total_good_match = 0
    total_correct = 0
    total_found = 0

    for k in to_evaluate_polygons:

        n_good_match = 0
        for p in to_evaluate_polygons[k]:
            n_good_match += p.get_count_match()

        if k in correct_polygons:
            n_correct = len(correct_polygons[k])
        else:
            n_correct = 0

        if k in to_evaluate_polygons:
            n_found = len(to_evaluate_polygons[k])
        else:
            n_found = 0

        total_good_match += n_good_match
        total_correct += n_correct
        total_found += n_found

        try:
            recall = round(n_good_match / n_correct, 3)
        except:
            recall = "label '{}' not present in the correct segmentation".format(k)

        precision = round(n_good_match / n_found, 3)

        val = {
            "n_good_match": n_good_match,
            "n_correct": n_correct,
            "n_found": n_found,
            "recall": recall,
            "precision": precision
        }

        performance[k] = val

    for k in correct_polygons:
        if k not in to_evaluate_polygons:
            n_good_match = 0
            n_correct = len(correct_polygons[k])
            n_found = 0

            total_good_match += n_good_match
            total_correct += n_correct
            total_found += n_found

            recall = round(n_good_match / n_correct, 3)
            precision = "label '{}' not present in your segmentation".format(k)

            val = {
                "n_good_match": n_good_match,
                "n_correct": n_correct,
                "n_found": n_found,
                "recall": recall,
                "precision": precision
            }

            performance[k] = val

    recall = round(total_good_match / total_correct, 3)
    precision = round(total_good_match / total_found, 3)

    val = {
        "n_good_match": total_good_match,
        "n_correct": total_correct,
        "n_found": total_found,
        "recall": recall,
        "precision": precision
    }

    performance['overall_performance'] = val

    result_path = os.path.join(result_path, 'performance_evaluation.json')
    with open(result_path, 'w') as file:
        file.write(json.dumps(performance, indent=4))

    return True
