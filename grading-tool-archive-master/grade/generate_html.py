#!/usr/bin/python3

from .tests import COMPLETE, ERROR, TIMEOUT, UNIMPLEMENTED
import webbrowser, tempfile, sys
import multiprocessing
from .subjective import SubjectiveCriteria

from io import StringIO

def runAllTests(functionTesterClasses, compilation=False, verbose=True):
    testers = []
    incomplete = False
    error = False
    for FunctionTester in functionTesterClasses:
        s = FunctionTester()
        if verbose: print(f'\nTesting {s.function_name}...')
        s.test(compilation)
        if s.result == UNIMPLEMENTED:
            if not s.isBonus:
                incomplete = True
        elif s.result != COMPLETE:
            error = True
        if verbose: print(f'{s.totalPoints()}/{s.maxPoints()}')
        testers.append(s)
    # FAIL 0, WARNING 1, SUCCESS 2
    if error:
        status = 0
    elif incomplete:
        status = 1
    else:
        status = 2
    return testers, status

def generateFullText(testers, title="Test Results", redact=False, github_link=None):
    totalScore = sum(tester.totalPoints() for tester in testers)
    maxScore = sum(tester.maxPoints()*(not tester.isBonus) for tester in testers)
    text = text = title
    if redact < 2: text += f' ({totalScore}/{maxScore})'
    if github_link: text += f'\n Source: {github_link}'
    for tester in testers:
        text += '\n\n'
        text += tester.generateText(redact)
    return text

def generateFullHTML(testers, title="Test Results", redact=False, github_link=None):
    html = '''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
        <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.blue_grey-indigo.min.css">
        <script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
            .mdl-layout__drawer .mdl-navigation .mdl-navigation__link .material-icons { margin-left: -24px; margin-right: 5px; }
            .is-small-screen .mdl-layout__drawer .mdl-navigation .mdl-navigation__link .material-icons { margin-left: 0px !important; }
            .pass { color: green !important; }
            .info { color: #F70 !important; }
            .error { color: red !important; }
            .timeout { color: red !important; }
            .unimplemented { color: #6AD !important; }
            .feedback { max-width: 1000px; }
            samp + .feedback { margin-top: 25px; }
            .feedback:not(:last-child) { margin-bottom: 15px; }
        </style>
        <title>'''+title+'''</title>
    </head>
    <body>
        <div class="mdl-layout mdl-js-layout mdl-layout--fixed-drawer">
            <div class="mdl-layout__drawer">
                <a class="mdl-layout-title" href="#top" style="text-decoration: none;">'''+title+'''</a>
                <nav class="mdl-navigation">
'''
    grand_total = 0
    grand_max = 0
    for s in testers:
        score = s.totalPoints()
        max_score = s.maxPoints()
        result_class = {COMPLETE: 'info', ERROR: 'error', TIMEOUT: 'timeout', UNIMPLEMENTED: 'unimplemented'}[s.result]
        result_icon = {COMPLETE: 'feedback', ERROR: 'error', TIMEOUT: 'notifications_active', UNIMPLEMENTED: 'more_horiz'}[s.result]
        if s.result == COMPLETE:
            if score >= max_score or not s.criteria_passed.symmetric_difference(s.criteria):
                result_class = 'pass'
                result_icon = 'check_circle'
            if redact == 2:
                result_class = 'unimplemented'
                result_icon = 'check_circle'
        grand_total += score
        if not s.isBonus:
            grand_max += max_score
        html += f'<a class="mdl-navigation__link {result_class}" href="#{s.function_name}">\n'
        html += f'<i class="material-icons">{result_icon}</i>\n'
        if len(s.function_name) < 13:
            censored_name = s.function_name
            addin = ''
        else:
            censored_name = s.function_name[:10]
            addin = '...'
        html += f'<code>{censored_name}</code>{addin}'
        if redact < 2: html += f' ({score}/{max_score})\n'
        html += '</a>\n'
    if github_link:
        if not '/tree/' in github_link: github_link_short = github_link
        else:
            github_link_before, github_link_after = github_link.split('/tree/')
            github_commit, github_assignment = github_link_after.split('/')
            github_link_short = f'{github_link_before}/tree/{github_commit[:8]}.../{github_assignment}'
    html += '''</nav>
        </div>
        <main class="mdl-layout__content mdl-color--grey-100">
            <div id="top"></div>
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col">
                    <h1>Test Results for '''+title+(f' ({grand_total}/{grand_max})' if redact<2 else '')+'''</h1>'''+(f'''
                    <h4>(Source: <a href="{github_link}" target="_blank">{github_link_short}</a>)</h4>''' if github_link else '')+'''
                </div>
'''
    for s in testers:
        html += s.generateHTML(redact)
    html += '''</div>
            </main>
        </div>
    </body>
</html>'''

    lines = html.split('\n')
    pleasant_html = ''
    indents = 0
    for line in lines:
        if not line.strip(): continue
        n_closed = line.count('</') # closed tags
        n_opened = line.count('<') - line.count('</') - line.count('<br>') - line.count('<meta') - line.count('<!') - line.count('/>') - line.count('<img') - line.count('<input') - line.count('<link') # opened tags
        n_diff = n_opened - n_closed
        if n_diff <= 0: indents += n_diff
        pleasant_html += '  '*indents
        pleasant_html += line.strip()
        pleasant_html += '\n'
        if n_diff > 0: indents += n_diff
    return pleasant_html

############################################
# The following is for use student-side    #
# (not used because the grading tool could #
#  help students work out the solution)    #
############################################

def displayHTML(html, path="results.html"):
    if not path:
        fd, path = tempfile.mkstemp()
        f = open(fd, 'w')
    else:
        f = open(path, 'w')
    f.write(html)
    f.close()
    webbrowser.open(path)

##################################################
# The following are used for server-side grading #
##################################################

def _safeGrade(folder, testSuite, title, compilation_test=False, redact=False, include_subjective=False, github_link=None, plaintext=False, verbose=False, pipe=None):
    sys.path.append(folder)
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    if include_subjective: testSuite = testSuite + [SubjectiveCriteria]
    testers, status = runAllTests(testSuite, compilation_test, verbose=verbose)

    student_output = sys.stdout.getvalue()[:1*1024*1024] # just first 1MB get returned
    sys.stdout = old_stdout
    sys.path.remove(folder)


    if plaintext:
        feedback = generateFullText(testers, title, redact, github_link)
    else:
        feedback = generateFullHTML(testers, title, redact, github_link)
    score = sum(tester.totalPoints() for tester in testers)
    plagiarism = bool(sum(tester.plagiarism_flag for tester in testers))
    if verbose: sys.stdout.write(student_output)
    if verbose: print(f'Score: {score}')

    if pipe is None:
        return score, plagiarism, status, feedback, student_output
    else:
        pipe.send(score)
        pipe.send(plagiarism)
        pipe.send(status)
        pipe.send(feedback)
        pipe.send(student_output)
        pipe.close()

def safeGrade(folder, testSuite, title, compilation_test=False, redact=False, include_subjective=False, github_link=None, plaintext=False, verbose=False):
    receive, send = multiprocessing.Pipe(False)

    p = multiprocessing.Process(target=_safeGrade, args=(folder, testSuite, title, compilation_test, redact, include_subjective, github_link, plaintext, verbose, send))
    p.daemon = False
    p.start()

    while p.exitcode is None and not receive.poll():
        p.join(.05)
    if receive.poll():
        score = receive.recv()
    else:
        raise RuntimeError("Child process unexpectedly terminated.")
    while p.exitcode is None and not receive.poll():
        p.join(.05)
    if receive.poll():
        plagiarism = receive.recv()
    else:
        raise RuntimeError("Child process unexpectedly terminated.")
    while p.exitcode is None and not receive.poll():
        p.join(.05)
    if receive.poll():
        status = receive.recv()
    else:
        raise RuntimeError("Child process unexpectedly terminated.")
    while p.exitcode is None and not receive.poll():
        p.join(.05)
    if receive.poll():
        feedback = receive.recv()
    else:
        raise RuntimeError("Child process unexpectedly terminated.")
    while p.exitcode is None and not receive.poll():
        p.join(.05)
    if receive.poll():
        student_output = receive.recv()
    else:
        raise RuntimeError("Child process unexpectedly terminated.")

    receive.close()

    return score, plagiarism, status, feedback, student_output

def defaultGrade(folder, testSuite, title, github_link):
    return safeGrade(folder, testSuite, title, github_link=github_link)

def defaultCompilationTest(folder, testSuite, title, github_link):
    return safeGrade(folder, testSuite, title, compilation_test=True, redact=2, github_link=github_link, plaintext=True)

#########################################################################
# The following are for use in batch scripts, such as re-grade scripts. #
#########################################################################

def batchGrade(folders, functionTesterClasses, title, include_subjective=False, startAt=0, verbose=True):
    for i, folder in enumerate(folders):
        if i < startAt: continue
        if verbose: print(f'Testing submission {i+1} of {len(folders)}...')
        score, plagiarism, status, feedback, student_output = safeGrade(folder, functionTesterClasses, title, False, include_subjective)
        open(folder+'/results.html', 'w').write(feedback)
        if verbose: print(f'Score: {score}\n')
