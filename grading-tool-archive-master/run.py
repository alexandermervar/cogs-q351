import sys
import argparse

commands = ['build', 'submit']

def build(args):
    sys.path.append(args.lib_folder)
    import grade
    test_case = __import__(f'test_{args.assignment_path}')

    results = grade.defaultCompilationTest(f"{args.student_folder}/{args.assignment_path}", test_case.testSuite, test_case.title, args.github_link)
    
    feedback, student_output = results[3:]
    with open(args.feedback_file, 'w') as f:
        f.write(feedback)
    with open(args.student_output_file, 'w') as f:
        f.write(student_output)
    print("\n".join([str(r) for r in results[:3]]) + "\nx", end='')
    return results

def submit(args):
    sys.path.append(args.lib_folder)
    import grade
    test_case = __import__(f'test_{args.assignment_path}')

    results = grade.defaultGrade(f"{args.student_folder}/{args.assignment_path}", test_case.testSuite, test_case.title, args.github_link)
    
    feedback, student_output = results[3:]
    with open(args.feedback_file, 'w') as f:
        f.write(feedback)
    with open(args.student_output_file, 'w') as f:
        f.write(student_output)
    print("\n".join([str(r) for r in results[:3]]) + "\nx", end='')
    return results

def build_parser(parser):
    parser.add_argument("student_folder", help="path to students submission folder")
    parser.add_argument("assignment_path", help="path to assignment.")
    parser.add_argument("feedback_file", help="path to feedback file.")
    parser.add_argument("student_output_file", help="path to student output file.")
    parser.add_argument("github_link", help="link to commit on github")
    parser.add_argument("lib_folder", help='library folder')

def submit_parser(parser):
    parser.add_argument("student_folder", help="path to students submission folder")
    parser.add_argument("assignment_path", help="path to assignment.")
    parser.add_argument("feedback_file", help="path to feedback file.")
    parser.add_argument("student_output_file", help="path to student output file.")
    parser.add_argument("github_link", help="link to commit on github")
    parser.add_argument("lib_folder", help='library folder')


def main():
    __globals__ = globals()
    descr = "run b351 test cases :)"
    parser = argparse.ArgumentParser(description=descr)
    subparsers = parser.add_subparsers()
    for cmd in commands:
        cmdf = __globals__[cmd]
        subp = subparsers.add_parser(cmd, help=cmdf.__doc__)
        __globals__[cmd + '_parser'](subp)
        subp.set_defaults(func=cmdf)
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.error("Please specify at least one command")


if __name__ == "__main__":
    main()
