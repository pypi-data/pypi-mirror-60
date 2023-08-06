from colours_library import colours
import coloursCLI
import argparse

import os
import sys
def recognizer():
    #initialize argpase obj
    parser = argparse.ArgumentParser(description=
                                    'Takes 2 arguments path_to_file - string,\n' +
                                    'number_of_args - integer naaajs')
    #add arguments
    #parser.add_argument('Path',
    #                     metavar='path',
    #                     type=str,
    #                     help='Path to the image')
    #
    #parser.add_argument('Number_of_args',
    #                     metavar='numb_of_colors',
    #                     type=int,
    #                     help='Number of most common colors')
    #args = parser.parse_args()
    #input_path = args.Path
    #input_numb = args.Number_of_args
    while True:
        try:
            path = input('Add path to the image. ')
            numb = input('How many most frequent colors? ')
            mcc = colours.MostCommonColor(path, int(numb))        
            output = mcc.produce()
            print(output)
            repeat = input('Do you want to repeat?\ny for yes \\ anything else for no ')
            if(repeat == 'y'):
                print('Let\'s go')
            else:
                break
        except FileNotFoundError:
            print('Seems like no such file exists ;/')
            print('try again')
        except TypeError:
            print('I work with jpg files only.')
            print('try again')
        except ValueError:
            print('No support for this color count.')
            print('try again')
    