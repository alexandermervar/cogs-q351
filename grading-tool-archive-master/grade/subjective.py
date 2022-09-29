#!/usr/bin/python3

from . import tests
import cgi

class Clarity(tests.Criterion):
    summary = 'Is clear and easy to read.'
    points = 15
    passByDefault = False

class ControlFlow(tests.Criterion):
    summary = 'Uses control flow paradigms appropriate to the tasks set.'
    points = 5
    passByDefault = False

class SyntaxFeatures(tests.Criterion):
    summary = 'Makes use of Python syntax features for elegant, functional code.'
    points = 5
    passByDefault = False

class SubjectiveCriteria(tests.CriterionTester):
    function_name = 'Subjective'
    def __init__(self):
        tests.CriterionTester.__init__(self, [], [Clarity, ControlFlow, SyntaxFeatures])
    def generateHTML(self, redact=False):
        ''' Generates HTML explaining the results of the most recent test. '''
        score = sum(i.points for i in self.criteria_passed)
        max_score = sum(i.points for i in self.criteria)
        html = f'<div class="mdl-cell mdl-cell--12-col" id="{self.function_name}">\n'
        html += f'<h2>Subjective Criteria: Grading Incomplete. ({score}/{max_score})</h2>\n'
        html += '<ul>\n'
        for criterion in self.criteria:
            html += '<li>\n'
            html += f'<h5> {cgi.escape(criterion.summary)} (?/{criterion.points})</h5>\n'

            html += '<div class="feedback">\n'
            html += 'Write feedback here.\n'
            html += '</div>\n'
            html += '</li>\n'
        html += '</ul>\n'
        html += '</div>\n'
        return html
