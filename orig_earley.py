#!/usr/bin/env python

import sys
import argparse
import math
import time


class Entry:
    index = 0
    RHS = []
    LHS = []
    left_pointer = None
    col_pointer = None
    weight = None

    def __init__(self, index, LHS, RHS, left_pointer, col_pointer, weight):
        self.index = index
        self.LHS = LHS
        self.RHS = RHS
        self.left_pointer = left_pointer
        self.col_pointer = col_pointer
        self.weight = weight

    def to_string(self): #for printing purposes
        return str(self.index) + " " + str(self.LHS) + " -> " + str(self.RHS)

class Chart:

    col_across = None
    hash = None

    def __init__ (self, sentence):

        self.col_across = []
        self.hash_col = {}
        for i in range(len(sentence.split())+1):
            self.col_across.append([])

    def add(self, cur_entry, index, location):

        if cur_entry.to_string() not in self.hash_col:
            self.col_across[index].append(cur_entry)
            self.hash_col[cur_entry.to_string()] = [cur_entry, location]
        else:
            if cur_entry.weight < self.hash_col[cur_entry.to_string()][0].weight:
                self.col_across[index][self.hash_col[cur_entry.to_string()][1]] = None
                self.col_across[index].append(cur_entry)
                self.hash_col[cur_entry.to_string()] = [cur_entry, location]

    def add_next(self, cur_entry, index):
        self.col_across[index].append(cur_entry)

    def add_next_hash(self, index):
        counter = 0
        for item in self.col_across[index]:
            if item.to_string() not in self.hash_col:
                self.hash_col[item.to_string()] = [item, counter]
            else:
                if item.weight < self.hash_col[item.to_string()][0].weight:
                    self.col_across[index][self.hash_col[item.to_string()][1]] = None
                    self.hash_col[item.to_string()] = [item, counter]
            counter += 1

def parse_grammar(file):

    f = open(file)
    rules = {}
    for line in f:
        split_line = line.split()

        if len(split_line) > 0:
            LHS = split_line[1]
            check = split_line[2:]

            if LHS not in rules:
                rules[LHS] = []

            weight = 0 - math.log(float(split_line[0]), 2)
            new_rule = list()
            new_rule.append(weight)
            new_rule.append(split_line[2:])
            rules[LHS].append(new_rule)

    return rules
    


def find_backpointer(entry):
    if entry is None:
        return ""
    ret_string = ""

    if not entry.RHS:
        if entry.left_pointer is None and entry.col_pointer is None:
            return str(entry.LHS) + " "

        ret_string += "(" + str(entry.LHS[0]) + " "
        if not entry.left_pointer is None:
            ret_string += str(find_backpointer(entry.left_pointer))
        if not entry.col_pointer is None:
            ret_string += str(find_backpointer(entry.col_pointer))
        ret_string += ")"
        return ret_string
    else:
        if not entry.left_pointer is None:
            ret_string += str(find_backpointer(entry.left_pointer))
        if not entry.col_pointer is None:
            ret_string += str(find_backpointer(entry.col_pointer))
        return ret_string


def pretty_print(ret_string):
    index = 0
    num_tab = 0
    while index < len(ret_string):
        sys.stdout.write(ret_string[index])  # we use sys.stdout.write to avoid the \n from print
        if ret_string[index] == "(":
            num_tab += 1
        elif ret_string[index] == ")":
            num_tab -= 1
            if index+1 < len(ret_string) and ret_string[index+1] != ')':
                if ret_string[index+1] == '(':
                    sys.stdout.write('\n' + num_tab*'\t')
                else:
                    sys.stdout.write('\n' + num_tab*'\t' + ret_string[index+1] + '\n' + num_tab*'\t')
                    index += 1
        index += 1


def parse_sentence(sentence, grammar):

    parse_chart = Chart(sentence)
    sentence_split = sentence.split()

    for item in grammar['ROOT']:
        entry1 = Entry(0, ['ROOT'], [item[1][0]], None, None, item[0])
        parse_chart.add(entry1, 0, 0)

    for i in range(len(sentence_split)+1):
        counter = 0
        curr_col = parse_chart.col_across[i]
        parse_chart.hash_col.clear()
        parse_chart.add_next_hash(i)
        while counter < len(curr_col):
            curr_entry = curr_col[counter]
            if curr_entry != None:
                if curr_entry.RHS:
                    if curr_entry.RHS[0] in grammar:
                        #predict
                            grammar_rule = grammar[curr_entry.RHS[0]]
                            for item in grammar_rule:
                                entry1 = Entry(i, [curr_entry.RHS[0]], item[1], None, None, item[0])
                                parse_chart.add(entry1, i, counter)
                    else:
                        #scan
                        if i < len(sentence_split):
                            if sentence_split[i] in curr_entry.RHS:
                                special_entry = Entry(0, sentence_split[i], [], None, None, 0)
                                next_col_entry = Entry(curr_entry.index, curr_entry.LHS[:], curr_entry.RHS[:], curr_entry, special_entry, curr_entry.weight)
                                next_col_entry.LHS.append(next_col_entry.RHS.pop(0))
                                parse_chart.add_next(next_col_entry, i+1)
                else:
                    #attach
                    for entry in parse_chart.col_across[curr_entry.index]:
                        if entry != None:
                            if entry.RHS and curr_entry.LHS[0] == entry.RHS[0]:
                                next_col_entry = Entry(entry.index, entry.LHS[:], entry.RHS[:], entry, curr_entry, entry.weight + curr_entry.weight)
                                next_col_entry.LHS.append(next_col_entry.RHS.pop(0))
                                parse_chart.add(next_col_entry, i, counter)
            counter += 1

    lowest_weight = float("inf")
    start = None


    for value in parse_chart.col_across[-1]:
        if value != None:
            if ('ROOT' in value.LHS) and (value.weight < lowest_weight):
                start = value
                lowest_weight = value.weight
            
    if start is None:
        print("NONE")
    else:
        #RECOGNIZED
        printme = find_backpointer(start)
        sys.stderr.write(printme + '\n')
        sys.stderr.write("Weight of best parse: " + str(lowest_weight) + '\n') 

    return parse_chart     


def main(argv):

    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar')
    parser.add_argument('sample')
    args = parser.parse_args()

    grammar = args.grammar
    sample = args.sample

    rules = parse_grammar(grammar)

    # create dictionary with grammar
    f = open(sample)
    counter = 0
    for line in f:
        if len(line.split()) > 0:
            maybe_chart = parse_sentence(line, rules)
            counter += 1
            
    sys.stderr.write("Time to parse: --- %s seconds ---\n" % (time.time() - start_time))


if __name__ == "__main__":
    main(sys.argv)
