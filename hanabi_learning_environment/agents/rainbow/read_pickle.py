import pickle
import matplotlib.pyplot as plt
import json
import argparse
import os.path

steps_per_iteration = 10000


def parse_data(name):
    with open('/home/uzi/hanabi_data/logs/{}'.format(name), 'rb') as file:
        self_eval = []
        self_eval_devs = []
        with_rules_eval = []
        with_rules_eval_devs = []
        steps = []
        d = pickle.load(file)
        prev_score = 0
        for i in d:
            if len(d[i]['eval_lenient_score']) != 1:
                # if d[i]['eval_lenient_score'][0] < prev_score*0.8:
                #     print("found a weird one at {} steps".format(int(i[len('iter'):]) * steps_per_iteration))
                #     print("value at spike is {}".format(d[i]['eval_lenient_score'][0]))
                #     continue
                steps.append(int(i[len('iter'):]) * steps_per_iteration)
                self_eval.append(d[i]['eval_lenient_score'][0])
                self_eval_devs.append(d[i]['eval_lenient_score_std_dev'][0])
                with_rules_eval.append(d[i]['eval_lenient_score'][1])
                with_rules_eval_devs.append(d[i]['eval_lenient_score_std_dev'][1])
                prev_score = d[i]['eval_lenient_score'][0]
        return steps, self_eval, self_eval_devs, with_rules_eval, with_rules_eval_devs


def get_baseline_data():
    steps, sp_data, sp_devs, mixed_data, mixed_devs = parse_data('baseline')
    return steps, sp_data


def print_score(file, zoom=False, draw_baseline_rainbow=True, draw_baseline_rules=True):
    steps, sp_data, sp_devs, mixed_data, mixed_devs = parse_data(file)
    # plot baseline Rainbow
    if draw_baseline_rainbow:
        baseline_iters, baseline_data = get_baseline_data()
        plt.plot(baseline_iters, baseline_data, label='Regular Rainbow self-play', alpha=0.6, color='c')
    # plot tested rainbow self-play data
    plt.plot(steps, sp_data, label='Tested Rainbow self-play', alpha=0.6, color='b')
    plt.fill_between(steps, [sp_data[i] - sp_devs[i] for i in range(0, len(sp_data))],
                     [sp_data[i] + sp_devs[i] for i in range(0, len(sp_data))], alpha=0.3, color='b')
    # plot rule-based agent data
    if draw_baseline_rules:
        rule_based_baseline = [19] * len(steps)
        rule_based_baseline_plus = [21] * len(steps)
        rule_based_baseline_minus = [17] * len(steps)
        plt.plot(steps, rule_based_baseline, label='Rule-based agent self-play', color='r')
        plt.fill_between(steps, rule_based_baseline_plus, rule_based_baseline_minus, alpha=0.3, color='r')
    # plot tested rainbow with rules-based agent data
    plt.plot(steps, mixed_data, label='Tested Rainbow with rules-based agent', alpha=0.6, color='m')
    plt.fill_between(steps, [mixed_data[i] - mixed_devs[i] for i in range(0, len(sp_data))],
                     [mixed_data[i] + mixed_devs[i] for i in range(0, len(sp_data))], alpha=0.3, color='m')
    plt.legend()
    plt.ylabel('Score')
    plt.xlabel('Steps')
    plt.ylim(0, 25)
    # fig_name = None
    if 'with_partner' in file:
        fig_name = '/home/uzi/hanabi_data/plots/with_partner/{}'.format(file)
    else:
        fig_name = '/home/uzi/hanabi_data/plots/{}'.format(file)
    if zoom:
        fig_name += ' zoomed'
    else:
        plt.xlim(0, 100000000)
    if not draw_baseline_rainbow and not draw_baseline_rules:
        fig_name += ' no baselines'
    plt.title('Mixed-Training, then Self-Play')
    plt.savefig(fig_name)
    plt.clf()


def print_baseline(zoom=False):
    steps, sp_data, sp_devs, mixed_data, mixed_devs = parse_data('baseline')
    rule_based_baseline = [19] * len(steps)
    rule_based_baseline_plus = [21] * len(steps)
    rule_based_baseline_minus = [17] * len(steps)
    # plot baseline rainbow self-play data
    plt.plot(steps, sp_data, label='Baseline Rainbow self-play', alpha=0.6, color='c')
    plt.fill_between(steps, [sp_data[i] - sp_devs[i] for i in range(0, len(sp_data))],
                     [sp_data[i] + sp_devs[i] for i in range(0, len(sp_data))], alpha=0.3, color='c')
    # plot rule-based agent data
    plt.plot(steps, rule_based_baseline, label='Rule-based agent self-play', color='r')
    plt.fill_between(steps, rule_based_baseline_plus, rule_based_baseline_minus, alpha=0.3, color='r')
    # plot tested rainbow with rules-based agent data
    plt.plot(steps, mixed_data, label='Baseline Rainbow with rules-based agent', alpha=0.6, color='m')
    plt.fill_between(steps, [mixed_data[i] - mixed_devs[i] for i in range(0, len(sp_data))],
                     [mixed_data[i] + mixed_devs[i] for i in range(0, len(sp_data))], alpha=0.3, color='m')
    plt.legend()
    plt.ylabel('Score')
    plt.xlabel('Steps')
    plt.ylim(0, 25)
    plt.title('Baseline')
    if not zoom:
        plt.xlim(0, 100000000)
        plt.savefig('/home/uzi/hanabi_data/plots/baseline.png')
    else:
        plt.savefig('/home/uzi/hanabi_data/plots/baseline zoomed.png')
    plt.clf()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('name', type=str)
    # args = parser.parse_args()
    # file = args.name
    file = '2_phase_short_3'
    print_score(file)
    print_score(file, draw_baseline_rainbow=False, draw_baseline_rules=False)
    # print_score(file, zoom=True)
    # print_baseline()
