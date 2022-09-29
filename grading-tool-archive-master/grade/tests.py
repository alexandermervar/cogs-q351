#!/usr/bin/python3

import sys
import importlib
import types
import time
import traceback
import threading
import html as cgi

PENDING = -1
COMPLETE = 0
ERROR   = 1
TIMEOUT = 2
UNIMPLEMENTED = 3

class Case:
    ''' Stores information about specific testing cases,
        often used by subroutines in a run procedure.
        Able to generate a string representation of itself
        in error situations.'''
    def __init__(self):
        ''' Stores requisite information;
            generally takes some arguments.'''
        pass
    def represent(self):
        ''' Uses relevant attributes to
            generate a short string
            describing the test case.'''
        return ''

class Criterion:
    ''' Class used to represent criteria;
        when initialized represents a failure
        of a criterion.'''
    passByDefault = True
    summary = ''
    neverRedact = False
    points = 0
    FAILURE = 0
    def __init__(self, case=None, details=None, problem_code=0):
        if type(case) == int:
            raise RuntimeWarning(f"You specified an integer for case. Perhaps you meant to provide a problem code?")
            if problem_code == 0:
                problem_code = case
        self.problem_code = problem_code
        self.case = case
        self.details = details
        self.__dict__.update(details) # this is new
    def representError(self, error):
        ''' Returns a multi-line string representing argument error. '''
        return ''.join(traceback.format_exception(error.__class__, error, error.__traceback__))
    def generateText(self):
        ''' Generates a string representing the error that occurred.
            Does not need to include the name or summary of the criterion.
            PLEASE OVERRIDE with more useful information.'''
        message = None
        for key in self.__class__.__dict__:
            if key == 'points': continue
            if type(self.__class__.__dict__[key]) == int and \
                self.__class__.__dict__[key] == self.problem_code:
                message = 'Problem code: %s\n' % key
        if message == None and self.problem_code == 0:
            message = 'Failed test\n'
        elif message == None:
            message = 'Problem code: %i\n' % self.problem_code
        if self.case:
            message += 'on case: %s\n' % self.case.represent()
        if self.details:
            message += 'with details: %s\n' % repr(self.details)
        return message
    def generateHTML(self):
        ''' Generates a string with HTML representing the error that occurred.
            Generally equivalent information to the result of generateText,
            but often more easy to follow. Will be placed into a div of
            indeterminate width and height.
            The automatic implementation should generally be good enough.'''
        html = cgi.escape(self.generateText().strip()).replace('\n','\n<br>').replace('\t', '&nbsp;'*4)
        while '<br> ' in html or '&nbsp; ' in html:
            html = html.replace('<br> ', '<br>&nbsp;').replace('&nbsp; ', '&nbsp;&nbsp;')
        if '\n' in html: html = '\n'+html+'\n'
        return '<samp>'+html+'</samp>'

class CriterionTester:
    ''' A class set up to test whether modules module_names pass criteria.
        CriterionTester.run should be overridden to check which criteria pass.
        fail_criterion can be called to indicate situations where a criterion failed.

        set_plagiarism_flag can be called to indicate student program behavior that
        should not occur; for example, if the signature of a function was changed
        from semester to semester. In our class, we automatically correct such cases
        and appear to score students well, silently setting the flag.

        If timeout (in s) is set, sets the result of the test as TIMEOUT when the
        timeout has been passed, but does not kill the subthread as this is not well-
        defined behavior cross-platform. However, all subthreads will be killed when
        the process exits. '''
    function_name = 'function'
    isBonus = False
    compilation_test_timeout = 0.05
    def __init__(self, module_names, criteria, timeout=1):
        self.module_names = module_names
        self.criteria = criteria
        self.timeout = timeout

        # prepares results
        self.result = PENDING

        self.criteria_passed = set()
        self.criteria_overridden = {}
        self.failures = []
        self.duration = 0
        self.exception = None
        self.implemented = False
        self.plagiarism_flag = False
    def load_modules(self):
        for module_name in self.module_names:
            if module_name in sys.modules: del sys.modules[module_name]
            module = importlib.import_module(module_name)
            importlib.reload(module)
            self.__dict__[module_name] = module
    def initialize_criteria(self):
        ''' Initializes the list of passed criteria to be those that
            are set as passByDefault. (Most criteria are pass by default,
            and removed from the list of passed criteria when they fail.)'''
        self.criteria_passed = set()
        for criterion in self.criteria:
            if criterion.passByDefault:
                self.criteria_passed.add(criterion)
    def set_score(self, criterion, score):
        ''' Overrides the score criterion will receive, regardless of
            whether the criterion is in the list of passed criteria. '''
        self.criteria_overridden[criterion] = score
    def pass_criterion(self, criterion):
        ''' Takes a criterion class and adds it to the list of passed criteria.'''
        self.criteria_passed.add(criterion)
    def fail_criterion(self, criterion, case=None, problem_code=0, important=False, no_feedback=False, **details):
        ''' Takes a criterion class, (potentially along with a test case,
            detail information, or subcode) and initializes it as a failure,
            adding it to the list of failures if it is unique or important is True.
            Removes the criterion class from the list of passed criteria.
            Returns True if the failure will be displayed to the user. '''
        self.criteria_passed.discard(criterion)

        if no_feedback: return

        found = False
        for failure in self.failures:
            if criterion == failure.__class__ and problem_code == failure.problem_code:
                found = True

        if not found or important:
            failure = criterion(case, details, problem_code)
            self.failures.append(failure)
            return True
        return False
    def fail_all_criteria(self):
        ''' Fails all criteria with no feedback. Generally used before aborting a run procedure. '''
        self.criteria_passed = set()
    def set_plagiarism_flag(self):
        self.plagiarism_flag = True
    def reraise(self, err, message):
        raise err.__class__(message) from err
    def _test(self, compilation_test=False):
        try: self.load_modules()
        except NotImplementedError: self.implemented = False
        except Exception as err: self.exception = err
        else:
            try: self.implemented = self.is_implemented()
            except NotImplementedError: self.implemented = False
            except Exception as err: self.exception = err
            else:
                if self.implemented:
                    try: self.run(compilation_test)
                    except NotImplementedError: self.implemented = False
                    except Exception as err: self.exception = err
    def test(self, compilation_test=False):
        self.initialize_criteria()
        self.failures = []
        self.exception = None
        self.implemented = True

        start_time = time.time()

        if compilation_test:
            timeout = self.compilation_test_timeout
        else:
            timeout = self.timeout

        if timeout is None:
            self._test()
            timed_out = False
        else:
            subtest = threading.Thread(target=self._test, args=(compilation_test,), daemon=True)
            subtest.start()
            subtest.join(timeout)
            if subtest.isAlive():
                timed_out = True
            else:
                timed_out = False
            # subtest isn't actually killed, but will be when the whole program ends.
        if timed_out:
            self.result = TIMEOUT
        elif not self.exception is None:
            self.result = ERROR
        elif not self.implemented:
            self.result = UNIMPLEMENTED
        else:
            self.result = COMPLETE

        self.duration = time.time() - start_time
    def is_implemented(self):
        ''' Should be implemented if unimplemented functions
            don't raise NotImplementedErrors. If implemented,
            usually checks that functions aren't returning None
            unexpectedly, etc... '''
        return True
    def run(self, compilation_test=False):
        ''' Initializes relevant classes (possibly multiple times)
            often subclassing them to isolate the relevant logic.
            Performs a set of tests on the classes (often iterating
            over a set of test cases), calling pass_criterion and
            fail_criterion as appropriate. Should test all criteria.

            If compilation_test is set to True, only run cursory tests
            designed to check whether the code is likely to throw an
            error or not. The timeout threshold is very low (50ms) in
            these cases. If you absolutely need extra time, set your
            subclass's compilation_test_timeout attribute (in s). '''
        pass
    def totalPoints(self):
        ''' Returns the sum of the point values of the passed criteria. '''
        if self.result != COMPLETE: return 0
        total = 0
        for criterion in self.criteria:
            if criterion in self.criteria_overridden:
                total += self.criteria_overridden[criterion]
            elif criterion in self.criteria_passed:
                total += criterion.points
        return total
    def maxPoints(self):
        ''' Returns the sum of the point values of all criteria. '''
        return sum(i.points for i in self.criteria)
    def generateText(self, redact=False):
        ''' Generates text explaining the results of the most recent test. '''
        max_score = self.maxPoints()
        text = self.function_name+'\n'
        if self.result == UNIMPLEMENTED:
            text += f'Not implemented.'
            if redact < 2: text += f' (Score: 0/{max_score})'
        elif self.result == TIMEOUT:
            text += f'Timed out.'
            if redact < 2: text += f' (Score: 0/{max_score})'
        elif self.result == ERROR:
            text += f'Error.'
            if redact < 2: text += f' (Score: 0/{max_score})'
            text += '\n'
            text += ''.join(traceback.format_exception(self.exception.__class__, self.exception, self.exception.__traceback__))
        elif self.result == COMPLETE:
            score = self.totalPoints()
            text += f'Test complete.'
            if redact < 2:  text += f' (Score: {score}/{max_score})'
        text += '\nTime elapsed: '+str(self.duration)[:5]+'s\n'
        if self.result == COMPLETE and redact < 2:
            if redact and score < max_score and self.criteria_passed.symmetric_difference(self.criteria):
                text += 'Your code did not meet all of our criteria.\nPlease check that it meets each of the following criteria.\n'
            text += 'Criteria:\n'
            for criterion in self.criteria:
                if redact and not criterion.neverRedact:
                    text += '* %s\n' % criterion.summary
                    continue
                # if we are not redacting
                if criterion in self.criteria_overridden:
                    text += '* %s (PASS - %i/%i)\n' % (criterion.summary, self.criteria_overridden[criterion], criterion.points)
                elif criterion in self.criteria_passed:
                    if criterion.points == 0 or redact:
                        text += '* %s (PASS)\n' % (criterion.summary)
                    else:
                        text += '* %s (PASS - %i/%i)\n' % (criterion.summary, criterion.points, criterion.points)
                else:
                    if criterion.points == 0 or redact:
                        text += '* %s (FAIL):\n' % (criterion.summary)
                    else:
                        text += '* %s (FAIL - %i/%i):\n' % (criterion.summary, 0, criterion.points)
                for failure in self.failures:
                    if failure.__class__ == criterion:
                        text += '  - %s\n' % failure.generateText().strip().replace('\n', '\n    ')
        return text.strip()
    def generateHTML(self, redact=False):
        ''' Generates HTML explaining the results of the most recent test. '''
        max_score = self.maxPoints()
        html = f'<div class="mdl-cell mdl-cell--12-col" id="{self.function_name}">\n'
        html += f'<h2><code>{self.function_name}</code>: '
        if self.result == UNIMPLEMENTED:
            html += f'Not implemented.'
            if redact < 2: html += f' (0/{max_score})'
        elif self.result == TIMEOUT:
            html += f'<span class="timeout">Timed out.</span>'
            if redact < 2: html += f' (0/{max_score})'
        elif self.result == ERROR:
            html += f'<span class="error">Error.</span>'
            if redact < 2: html += f' (0/{max_score})'
        elif self.result == COMPLETE and redact < 2:
            score = self.totalPoints()
            if score >= max_score or not self.criteria_passed.symmetric_difference(self.criteria):
                html += 'Pass. '
            else:
                html += '<span class="info">Issues detected.</span> '
            html += f' ({score}/{max_score})'
        elif self.result == COMPLETE:
            html += 'Test complete.'
        html += '</h2>\n'
        html += '<h4>Time elapsed: '+str(self.duration)[:5]+'s</h4>\n'
        if self.result == ERROR:
            html += '<samp>\n'
            error_text = ''.join(cgi.escape(line) for line in traceback.format_exception(self.exception.__class__, self.exception, self.exception.__traceback__))
            error_text = error_text.strip().replace('\n', '\n<br>')
            while '<br> ' in error_text or '&nbsp; ' in error_text:
                error_text = error_text.replace('<br> ', '<br>&nbsp;').replace('&nbsp; ', '&nbsp;&nbsp;')
            html += error_text+'\n'
            html += '</samp>\n'
        if self.result == COMPLETE and redact < 2:
            if redact and score < max_score and self.criteria_passed.symmetric_difference(self.criteria):
                html += '<h4>Please check that your code meets each of the following criteria:</h4>'
            html += '<ul>\n'
            for criterion in self.criteria:
                html += '<li>\n'
                html += '<h5>'
                html += cgi.escape(criterion.summary)

                if redact and not criterion.neverRedact:
                    html += '</h5>\n</li>\n'
                    continue


                if criterion in self.criteria_overridden:
                    html += f' ({self.criteria_overridden[criterion]}/{criterion.points})'
                elif criterion in self.criteria_passed:
                    if criterion.points == 0 or redact:
                        html += ' (PASS)'
                    else:
                        html += f' (PASS: {criterion.points}/{criterion.points})'
                else:
                    if criterion.points == 0 or redact:
                        html += ' <span class="error">(FAIL)</span>'
                    else:
                        html += f' <span class="error">(FAIL: 0/{criterion.points})</span>'

                html += '</h5>\n'

                for failure in self.failures:
                    if failure.__class__ == criterion:
                        html += '<div class="feedback">\n'
                        try:
                            html += failure.generateHTML()+'\n'
                        except Exception as error:
                            print('Look, an unladen European error flew by!')
                            print(''.join(traceback.format_exception(error.__class__, error, error.__traceback__)))
                            html += 'Unfortunately an error occurred while generating feedback. Please contact a course staff member as soon as possible to fix this issue.\n'
                        html += '</div>\n'
                html += '</li>\n'
            html += '</ul>\n'
        html += '</div>\n'
        return html
