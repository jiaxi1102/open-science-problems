// Independent exhaustive verifier for the strengthened KG(8,2) obstruction.
//
// This program does not share implementation code with the Lean generator.
// It fixes the first double-star core to {0,1} by S_8 transitivity, enumerates
// all C(13,11)=78 choices for its 11-set, all 28*C(13,11)=2184 choices for
// the opposite 11-set, and solves the remaining 420 not-all-equal triangle
// clauses by a complete DPLL search with unit propagation.
//
// Expected terminal line:
//   UNSAT k=11 tested=170352 overlap=129666 nodes=40027816

#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <vector>

namespace {

constexpr int kGroundVertices = 8;
constexpr int kKneserVertices = 28;
constexpr int kKneserEdges = 210;
constexpr int kTargetSize = 11;

struct NAE3Solver {
  explicit NAE3Solver(std::vector<std::array<int, 3>> clauses)
      : clauses_(std::move(clauses)), occurrences_(kKneserEdges) {
    for (int clause = 0; clause < static_cast<int>(clauses_.size()); ++clause) {
      for (int variable : clauses_[clause]) {
        occurrences_[variable].push_back(clause);
      }
    }
  }

  bool solve(const std::vector<std::pair<int, int>>& forced) {
    values_.fill(-1);
    trail_.clear();
    nodes = 0;
    std::deque<int> queue;
    for (const auto& [variable, value] : forced) {
      if (!assign(variable, value, queue)) return false;
    }
    if (!propagate(queue)) return false;
    return dfs();
  }

  std::int64_t nodes = 0;

 private:
  bool assign(int variable, int value, std::deque<int>& queue) {
    if (values_[variable] != -1) return values_[variable] == value;
    values_[variable] = static_cast<std::int8_t>(value);
    trail_.push_back(variable);
    queue.push_back(variable);
    return true;
  }

  bool propagate(std::deque<int>& queue) {
    while (!queue.empty()) {
      const int variable = queue.front();
      queue.pop_front();
      for (int clause_index : occurrences_[variable]) {
        const auto clause = clauses_[clause_index];
        int zeros = 0;
        int ones = 0;
        int unassigned = 0;
        int unassigned_variable = -1;
        for (int x : clause) {
          if (values_[x] == -1) {
            ++unassigned;
            unassigned_variable = x;
          } else if (values_[x] == 0) {
            ++zeros;
          } else {
            ++ones;
          }
        }
        if (unassigned == 0 && (zeros == 3 || ones == 3)) return false;
        if (unassigned == 1) {
          if (zeros == 2 && !assign(unassigned_variable, 1, queue)) return false;
          if (ones == 2 && !assign(unassigned_variable, 0, queue)) return false;
        }
      }
    }
    return true;
  }

  int choose_variable() const {
    int best = -1;
    int best_score = -1;
    for (int variable = 0; variable < kKneserEdges; ++variable) {
      if (values_[variable] != -1) continue;
      int score = 0;
      for (int clause_index : occurrences_[variable]) {
        int zeros = 0;
        int ones = 0;
        int unassigned = 0;
        for (int x : clauses_[clause_index]) {
          if (values_[x] == -1) {
            ++unassigned;
          } else if (values_[x] == 0) {
            ++zeros;
          } else {
            ++ones;
          }
        }
        if (!(zeros && ones)) score += 4 - unassigned;
      }
      if (score > best_score) {
        best_score = score;
        best = variable;
      }
    }
    return best;
  }

  bool dfs() {
    ++nodes;
    const int variable = choose_variable();
    if (variable < 0) return true;
    const std::size_t mark = trail_.size();
    for (int value = 0; value <= 1; ++value) {
      std::deque<int> queue;
      if (assign(variable, value, queue) && propagate(queue) && dfs()) return true;
      while (trail_.size() > mark) {
        values_[trail_.back()] = -1;
        trail_.pop_back();
      }
    }
    return false;
  }

  std::vector<std::array<int, 3>> clauses_;
  std::vector<std::vector<int>> occurrences_;
  std::array<std::int8_t, kKneserEdges> values_{};
  std::vector<int> trail_;
};

std::vector<std::vector<int>> choose_subsets(const std::vector<int>& universe,
                                              int size) {
  std::vector<std::vector<int>> result;
  std::vector<int> selected;
  std::function<void(int, int)> visit = [&](int start, int left) {
    if (left == 0) {
      result.push_back(selected);
      return;
    }
    for (int i = start; i <= static_cast<int>(universe.size()) - left; ++i) {
      selected.push_back(universe[i]);
      visit(i + 1, left - 1);
      selected.pop_back();
    }
  };
  visit(0, size);
  return result;
}

}  // namespace

int main() {
  std::vector<std::pair<int, int>> ground_pairs;
  for (int i = 0; i < kGroundVertices; ++i) {
    for (int j = i + 1; j < kGroundVertices; ++j) {
      ground_pairs.push_back({i, j});
    }
  }

  auto disjoint = [&](int a, int b) {
    const auto [x, y] = ground_pairs[a];
    const auto [u, v] = ground_pairs[b];
    return x != u && x != v && y != u && y != v;
  };

  std::vector<std::pair<int, int>> kneser_edges;
  std::map<std::pair<int, int>, int> edge_id;
  for (int i = 0; i < kKneserVertices; ++i) {
    for (int j = i + 1; j < kKneserVertices; ++j) {
      if (disjoint(i, j)) {
        edge_id[{i, j}] = static_cast<int>(kneser_edges.size());
        kneser_edges.push_back({i, j});
      }
    }
  }

  std::vector<std::array<int, 3>> triangles;
  for (int a = 0; a < kKneserVertices; ++a) {
    for (int b = a + 1; b < kKneserVertices; ++b) {
      for (int c = b + 1; c < kKneserVertices; ++c) {
        if (disjoint(a, b) && disjoint(a, c) && disjoint(b, c)) {
          triangles.push_back(
              {edge_id.at({a, b}), edge_id.at({a, c}), edge_id.at({b, c})});
        }
      }
    }
  }

  std::vector<std::vector<int>> double_stars;
  for (const auto& [x, y] : ground_pairs) {
    std::vector<int> star;
    for (int vertex = 0; vertex < kKneserVertices; ++vertex) {
      const auto [a, b] = ground_pairs[vertex];
      if (a == x || b == x || a == y || b == y) star.push_back(vertex);
    }
    if (star.size() != 13) return 2;
    double_stars.push_back(std::move(star));
  }

  if (ground_pairs.size() != 28 || kneser_edges.size() != 210 ||
      triangles.size() != 420 || double_stars.size() != 28) {
    return 3;
  }

  const auto first_sets = choose_subsets(double_stars[0], kTargetSize);
  std::vector<std::vector<int>> second_sets;
  for (const auto& star : double_stars) {
    const auto subsets = choose_subsets(star, kTargetSize);
    second_sets.insert(second_sets.end(), subsets.begin(), subsets.end());
  }
  if (first_sets.size() != 78 || second_sets.size() != 2184) return 4;

  auto induced_kneser_edges = [&](const std::vector<int>& selected) {
    std::vector<int> result;
    for (int i = 0; i < static_cast<int>(selected.size()); ++i) {
      for (int j = i + 1; j < static_cast<int>(selected.size()); ++j) {
        int a = selected[i];
        int b = selected[j];
        if (a > b) std::swap(a, b);
        const auto found = edge_id.find({a, b});
        if (found != edge_id.end()) result.push_back(found->second);
      }
    }
    return result;
  };

  std::vector<std::vector<int>> first_internal;
  std::vector<std::vector<int>> second_internal;
  for (const auto& set : first_sets) first_internal.push_back(induced_kneser_edges(set));
  for (const auto& set : second_sets) second_internal.push_back(induced_kneser_edges(set));

  NAE3Solver solver(triangles);
  std::int64_t tested = 0;
  std::int64_t immediate_overlap = 0;
  std::int64_t total_nodes = 0;
  const auto start = std::chrono::steady_clock::now();

  for (int ai = 0; ai < static_cast<int>(first_sets.size()); ++ai) {
    std::array<bool, kKneserEdges> forced_blue{};
    for (int edge : first_internal[ai]) forced_blue[edge] = true;

    for (int bi = 0; bi < static_cast<int>(second_sets.size()); ++bi) {
      ++tested;
      bool clash = false;
      std::vector<std::pair<int, int>> forced;
      for (int edge : first_internal[ai]) forced.push_back({edge, 1});
      for (int edge : second_internal[bi]) {
        if (forced_blue[edge]) {
          clash = true;
          break;
        }
        forced.push_back({edge, 0});
      }
      if (clash) {
        ++immediate_overlap;
        continue;
      }
      if (solver.solve(forced)) {
        std::cout << "SAT k=" << kTargetSize << " ai=" << ai << " bi=" << bi
                  << "\n";
        return 1;
      }
      total_nodes += solver.nodes;
    }
  }

  const double seconds = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - start).count();
  std::cout << "UNSAT k=" << kTargetSize << " tested=" << tested
            << " overlap=" << immediate_overlap << " nodes=" << total_nodes
            << " seconds=" << seconds << "\n";

  return (tested == 170352 && immediate_overlap == 129666 &&
          total_nodes == 40027816)
             ? 0
             : 5;
}
