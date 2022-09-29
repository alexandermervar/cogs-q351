#!/usr/bin/python3

import inspect

def check_a5(tester, a5):
    if hasattr(a5, 'get_entropy') and not hasattr(a5, 'calc_entropy'):
        tester.set_plagiarism_flag()
        a5.calc_entropy = a5.get_entropy
        
    if hasattr(a5, 'entropy') and not hasattr(a5, 'calc_entropy'):
    	tester.set_plagiarism_flag()
    	a5.calc_entropy = a5.entropy
    	
    if hasattr(a5, 'get_information_gain') and not hasattr(a5, 'calc_information_gain'):
        tester.set_plagiarism_flag()
        a5.calc_information_gain = a5.get_information_gain
    
    if hasattr(a5, 'information_gain') and not hasattr(a5, 'calc_information_gain'):
    	tester.set_plagiarism_flag()
    	a5.calc_information_gain = a5.information_gain
