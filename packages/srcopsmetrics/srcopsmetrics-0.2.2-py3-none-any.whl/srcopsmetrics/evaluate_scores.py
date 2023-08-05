#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019, 2020 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Reviewer Technical and Social Score."""

import logging
import os
import json
import time
import itertools
from datetime import timedelta
from datetime import datetime

from typing import Tuple, List
import numpy as np
import pandas as pd

from pathlib import Path
from collections import Counter

from srcopsmetrics.pre_processing import retrieve_knowledge
from srcopsmetrics.pre_processing import pre_process_project_data, pre_process_contributors_data
from srcopsmetrics.utils import convert_num2label, convert_score2num


_LOGGER = logging.getLogger(__name__)

BOTS_NAMES = ["sesheta", "dependencies[bot]", "dependabot[bot]", "review-notebook-app[bot]"]

pd.set_option("display.max_columns", 500)


def evaluate_contributor_technical_score(
    contributions: List[float],
    weighting_factors: List[float]
) -> float:
    """Evaluate contributor final score."""
    final_score = 1
    for contribution, w_factor in zip(contributions, weighting_factors):
        final_score += contribution * w_factor
    return final_score


def evaluate_reviewers_scores(project: Tuple[str, str], number_reviewer: int = 2):
    """Evaluate statistics from the knowledge of the bot and provide number of reviewers.

    :project: repository to be analyzed (e.g. (thoth-station, performance))
    :param number_reviewer: number of reviewers to select
    """
    knowledge_path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    data = retrieve_knowledge(knowledge_path=knowledge_path, project=project)
    if not data:
        return {}

    now_time = datetime.now()

    projects_reviews_data = pre_process_project_data(data=data)

    # Project statistics
    project_commits_number = sum([pr["commits_number"] for pr in data.values()])
    project_prs_number = len(data)
    project_prs_reviewed_number = len(projects_reviews_data["MTTR"])
    project_mtfr = projects_reviews_data["MTTFR"][-1]
    project_mttr = projects_reviews_data["MTTR"][-1]
    project_reviews_length_score = projects_reviews_data["median_pr_length_score"]

    project_last_review = projects_reviews_data["last_review_time"]
    project_time_since_last_review = now_time - datetime.fromtimestamp(project_last_review)

    project_data = pd.DataFrame(
        [
            (
                project,
                project_prs_number,
                project_commits_number,
                project_prs_reviewed_number,
                str(timedelta(hours=project_mtfr)),
                str(timedelta(hours=project_mttr)),
            )
        ],
        columns=[
            "Repository",
            "PullRequest n.",
            "Commits n.",
            "PullRequestRev n.",  # Pull requests reviewed
            "MTTFR",  # Median Time to First Review
            "MTTR",  # Median Time to Review
        ],
    )
    _LOGGER.info("-------------------------------------------------------------------------------")
    print(project_data)
    _LOGGER.info("-------------------------------------------------------------------------------")

    contributors = sorted(projects_reviews_data["contributors"])
    contributor_data = []
    scores_data = []

    # Contributors that reviewed and that didn't reviewed
    contributors_reviews_data = pre_process_contributors_data(
        data=data, contributors=[c for c in contributors if c not in BOTS_NAMES]
    )

    for contributor in contributors:

        _LOGGER.debug(f"Analyzing contributor: {contributor}")
        if contributor in contributors_reviews_data.keys() and contributor not in BOTS_NAMES:

            contributor_commits_number = sum(
                [pr["commits_number"] for pr in data.values() if pr["created_by"] == contributor]
            )

            contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    contributor_prs_number += 1

            contributor_prs_reviewed_number = len(contributors_reviews_data[contributor]["reviews"])
            contributor_median_pr_length = contributors_reviews_data[contributor]["median_pr_length"]
            contributor_reviews_number = contributors_reviews_data[contributor]["number_reviews"]
            contributor_reviews_length = contributors_reviews_data[contributor]["median_review_length"]
            contributor_reviews_length_score = contributors_reviews_data[contributor]["median_pr_length_score"]
            contributor_mtfr = contributors_reviews_data[contributor]["MTTFR"][-1]
            contributor_mttr = contributors_reviews_data[contributor]["MTTR"][-1]

            contributor_last_review = contributors_reviews_data[contributor]["last_review_time"]

            contributor_time_last_review = now_time - datetime.fromtimestamp(contributor_last_review)

            contributor_data.append(
                (
                    contributor,
                    contributor_prs_number,
                    contributor_prs_number / project_prs_number * 100,
                    contributor_prs_reviewed_number,
                    contributor_prs_reviewed_number / project_prs_reviewed_number * 100,
                    contributor_median_pr_length,
                    contributor_reviews_number,
                    contributor_reviews_length,
                    str(timedelta(hours=contributor_mtfr)),
                    str(timedelta(hours=contributor_mttr)),
                    contributor_time_last_review,
                    contributor_commits_number,
                    contributor_commits_number / project_commits_number * 100,
                    "N",
                )
            )

            # Contributions to final score:
            contributions = []

            # 1: Number of PR reviewed respect to total number of PR reviewed by the team.
            contributions.append(contributor_prs_number / project_prs_number)

            # 2: Median time to review a PR by reviewer respect to team repostiory MTTR.
            contributions.append(timedelta(hours=project_mttr) / timedelta(hours=contributor_mttr))

            # 3: Median length of PR reviewed respect to the median length of PR in project.
            contributions.append(contributor_reviews_length_score / project_reviews_length_score)

            # 4: Number of commits respect to the total number of commits in the repository.
            contributions.append(contributor_commits_number / project_commits_number)

            # 5: Time since last review respect to project last review.
            contributions.append(
                project_time_since_last_review.total_seconds() / contributor_time_last_review.total_seconds()
            )

            # TODO 6: Number of issue closed by a PR reviewed from an author respect to total number of issue closed.
            contributions.append(1)

            final_score = evaluate_contributor_technical_score(
                contributions=contributions,
                weighting_factors=[1, 1, 1, 1, 1, 1]
            )

            scores_data.append(
                (
                    contributor,
                    contributions[0],
                    contributions[1],
                    contributions[2],
                    contributions[3],
                    contributions[4],
                    contributions[5],
                    final_score,
                )
            )

        elif contributor in BOTS_NAMES:

            bot_contributor_commits_number = sum(
                [pr["commits_number"] for pr in data.values() if pr["created_by"] == contributor]
            )

            bot_contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    bot_contributor_prs_number += 1

            contributor_data.append(
                (
                    contributor,
                    bot_contributor_prs_number,
                    bot_contributor_prs_number / project_prs_number * 100,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    bot_contributor_commits_number,
                    contributor_commits_number / project_commits_number * 100,
                    "Y",
                )
            )

        else:

            contributor_commits_number = sum(
                [pr["commits_number"] for pr in data.values() if pr["created_by"] == contributor]
            )

            contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    contributor_prs_number += 1

            contributor_data.append(
                (
                    contributor,
                    contributor_prs_number,
                    contributor_prs_number / project_prs_number * 100,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    contributor_commits_number,
                    contributor_commits_number / project_commits_number * 100,
                    "N",
                )
            )

    contributors_data = pd.DataFrame(
        contributor_data,
        columns=[
            "Contributor",
            "PR n.",        # Pull Request number
            "PR %",         # Pull Request percentage respect to total
            "PRRev n.",     # Pull Request Reviewed number
            "PRRev %",      # Pull Request Reviewed percentage respect to total
            "MPRLen",       # Median Pull Request Reviewed Length
            "Rev n.",       # Reviews number
            "MRL",          # Median Review Length (Word count based)
            "MTTFR",        # Median Time to First Review
            "MTTR",         # Median Time to Review
            "TLR",          # Time Last Review [hr]
            "Comm n.",      # Commits number
            "Comm %",       # Commits percentage
            "Bot",          # Is a bot?
        ],
    )
    print()
    print(contributors_data)

    contributors_score_data = pd.DataFrame(
        scores_data,
        columns=[
            "Contributor",
            "PRs reviewed score",
            "MTTR score",
            "PR length score",
            "Commits score",
            "Time Last review score",
            "TTCI score",
            "Technical score",  # Contributor Final TechnicalScore
        ],
    )

    print()
    sorted_reviewers = contributors_score_data.sort_values(by=["Technical score"], ascending=False)
    print(sorted_reviewers)

    print()
    _LOGGER.info(f"Number of reviewers requested: {number_reviewer}")
    _LOGGER.info(f"Reviewers: {sorted_reviewers['Contributor'].head(number_reviewer).values}")
