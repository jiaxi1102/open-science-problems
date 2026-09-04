#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

using Edge = std::pair<int, int>;

/*
  Exact branch-and-propagate solver for not-all-equal constraints on triples.
  This implementation is intentionally independent of the Lean generator.
*/
class NAE3Solver {
 public:
  static constexpr int kVariables = 210;

  explicit NAE3Solver(const std::vector<std::array<int, 3>>& triangles)
      : triangles_(triangles) {
    values_.fill(-1);
    for (int i = 0; i < static_cast<int>(triangles_.size()); ++i) {
      for (int variable : triangles_[i]) {
        incident_[variable].push_back(i);
      }
    }
  }

  bool Solve(const std::map<int, int>& forced) {
    Reset();
    for (const auto& [variable, value] : forced) {
      if (!Enqueue(variable, value)) {
        return false;
      }
    }
    return Dfs();
  }

  bool CheckCurrentModel(const std::map<int, int>& forced) const {
    for (const auto& [variable, value] : forced) {
      if (values_[variable] != value) {
        return false;
      }
    }
    for (const auto& triangle : triangles_) {
      const int a = values_[triangle[0]];
      const int b = values_[triangle[1]];
      const int c = values_[triangle[2]];
      if (a < 0 || b < 0 || c < 0 || (a == b && b == c)) {
        return false;
      }
    }
    return true;
  }

  std::uint64_t nodes() const { return nodes_; }

 private:
  void Reset() {
    for (int variable : trail_) {
      values_[variable] = -1;
    }
    trail_.clear();
    nodes_ = 0;
  }

  bool Enqueue(int variable, int value) {
    if (values_[variable] != -1) {
      return values_[variable] == value;
    }
    values_[variable] = static_cast<std::int8_t>(value);
    trail_.push_back(variable);
    return true;
  }

  bool Propagate(std::size_t queue_index = 0) {
    while (queue_index < trail_.size()) {
      const int variable = trail_[queue_index++];
      for (int triangle_index : incident_[variable]) {
        const auto& triangle = triangles_[triangle_index];
        int unassigned = -1;
        int unassigned_count = 0;
        int zeros = 0;
        int ones = 0;
        for (int other : triangle) {
          if (values_[other] == -1) {
            unassigned = other;
            ++unassigned_count;
          } else if (values_[other] == 0) {
            ++zeros;
          } else {
            ++ones;
          }
        }
        if (unassigned_count == 0) {
          if (zeros == 3 || ones == 3) {
            return false;
          }
        } else if (unassigned_count == 1) {
          if (zeros == 2 && !Enqueue(unassigned, 1)) {
            return false;
          }
          if (ones == 2 && !Enqueue(unassigned, 0)) {
            return false;
          }
        }
      }
    }
    return true;
  }

  int ChooseVariable() const {
    int best_variable = -1;
    int best_score = -1;
    for (int variable = 0; variable < kVariables; ++variable) {
      if (values_[variable] != -1) {
        continue;
      }
      int score = 0;
      for (int triangle_index : incident_[variable]) {
        const auto& triangle = triangles_[triangle_index];
        int zeros = 0;
        int ones = 0;
        int unassigned = 0;
        for (int other : triangle) {
          if (values_[other] == -1) {
            ++unassigned;
          } else if (values_[other] == 0) {
            ++zeros;
          } else {
            ++ones;
          }
        }
        if (zeros != 0 && ones != 0) {
          continue;
        }
        score += (unassigned == 3 ? 1 : unassigned == 2 ? 5 : 20);
      }
      if (score > best_score) {
        best_score = score;
        best_variable = variable;
      }
    }
    return best_variable;
  }

  bool Dfs() {
    ++nodes_;
    if (!Propagate()) {
      return false;
    }
    const int variable = ChooseVariable();
    if (variable < 0) {
      return true;
    }

    int pressure[2] = {0, 0};
    for (int triangle_index : incident_[variable]) {
      for (int other : triangles_[triangle_index]) {
        if (other != variable && values_[other] != -1) {
          ++pressure[values_[other]];
        }
      }
    }
    const int first_value = pressure[0] >= pressure[1] ? 1 : 0;
    const std::size_t mark = trail_.size();
    for (int branch = 0; branch < 2; ++branch) {
      const int value = branch == 0 ? first_value : 1 - first_value;
      if (Enqueue(variable, value) && Dfs()) {
        return true;
      }
      while (trail_.size() > mark) {
        values_[trail_.back()] = -1;
        trail_.pop_back();
      }
    }
    return false;
  }

  std::vector<std::array<int, 3>> triangles_;
  std::array<std::vector<int>, kVariables> incident_;
  std::array<std::int8_t, kVariables> values_;
  std::vector<int> trail_;
  std::uint64_t nodes_ = 0;
};

int main() {
  std::vector<Edge> vertices;
  for (int i = 0; i < 8; ++i) {
    for (int j = i + 1; j < 8; ++j) {
      vertices.push_back({i, j});
    }
  }
  const auto disjoint = [&](int a, int b) {
    const auto x = vertices[a];
    const auto y = vertices[b];
    return x.first != y.first && x.first != y.second &&
           x.second != y.first && x.second != y.second;
  };

  std::vector<Edge> edges;
  int edge_id[28][28];
  for (auto& row : edge_id) {
    std::fill(std::begin(row), std::end(row), -1);
  }
  for (int i = 0; i < 28; ++i) {
    for (int j = i + 1; j < 28; ++j) {
      if (disjoint(i, j)) {
        edge_id[i][j] = edge_id[j][i] = static_cast<int>(edges.size());
        edges.push_back({i, j});
      }
    }
  }

  std::vector<std::array<int, 3>> triangles;
  for (int a = 0; a < 28; ++a) {
    for (int b = a + 1; b < 28; ++b) {
      for (int c = b + 1; c < 28; ++c) {
        if (disjoint(a, b) && disjoint(a, c) && disjoint(b, c)) {
          triangles.push_back(
              {edge_id[a][b], edge_id[a][c], edge_id[b][c]});
        }
      }
    }
  }
  if (vertices.size() != 28 || edges.size() != 210 ||
      triangles.size() != 420) {
    std::cerr << "unexpected KG(8,2) counts\n";
    return 3;
  }

  const auto vertex_id = [&](int a, int b) {
    if (a > b) {
      std::swap(a, b);
    }
    return static_cast<int>(
        std::find(vertices.begin(), vertices.end(), Edge{a, b}) -
        vertices.begin());
  };

  const std::vector<Edge> cores = vertices;
  std::map<Edge, std::vector<int>> double_stars;
  for (const auto& core : cores) {
    for (int i = 0; i < 28; ++i) {
      const auto edge = vertices[i];
      if (edge.first == core.first || edge.second == core.first ||
          edge.first == core.second || edge.second == core.second) {
        double_stars[core].push_back(i);
      }
    }
    if (double_stars[core].size() != 13) {
      std::cerr << "unexpected double-star size\n";
      return 4;
    }
  }

  // Solver sanity checks: a single forced-monochromatic triple and the Fano
  // plane are unsatisfiable; the KG(8,2) NAE instance itself is satisfiable.
  {
    NAE3Solver one_triangle({{0, 1, 2}});
    if (one_triangle.Solve({{0, 0}, {1, 0}, {2, 0}})) {
      std::cerr << "solver self-test failed on one forced triangle\n";
      return 5;
    }
    const std::vector<std::array<int, 3>> fano = {
        {0, 1, 2}, {0, 3, 4}, {0, 5, 6}, {1, 3, 5},
        {1, 4, 6}, {2, 3, 6}, {2, 4, 5}};
    NAE3Solver fano_solver(fano);
    if (fano_solver.Solve({})) {
      std::cerr << "solver self-test failed on the Fano plane\n";
      return 6;
    }
  }

  NAE3Solver solver(triangles);
  if (!solver.Solve({}) || !solver.CheckCurrentModel({})) {
    std::cerr << "base KG(8,2) triangle-free coloring was not recovered\n";
    return 7;
  }

  struct Representative {
    std::string name;
    int first_deleted;
    int second_deleted;
  };
  const std::vector<Representative> representatives = {
      {"center_spoke", vertex_id(0, 1), vertex_id(0, 2)},
      {"same_center_spokes", vertex_id(0, 2), vertex_id(0, 3)},
      {"opposite_same_leaf", vertex_id(0, 2), vertex_id(1, 2)},
      {"opposite_distinct_leaves", vertex_id(0, 2), vertex_id(1, 3)}};

  // Check the four stabilizer-orbit types partition all C(13,2)=78 deletions.
  std::map<std::string, int> orbit_sizes;
  const auto& fixed_double_star = double_stars[{0, 1}];
  for (int i = 0; i < 13; ++i) {
    for (int j = i + 1; j < 13; ++j) {
      const auto a = vertices[fixed_double_star[i]];
      const auto b = vertices[fixed_double_star[j]];
      std::string type;
      if (a == Edge{0, 1} || b == Edge{0, 1}) {
        type = "center_spoke";
      } else {
        const int center_a = a.first <= 1 ? a.first : a.second;
        const int center_b = b.first <= 1 ? b.first : b.second;
        const int leaf_a = a.first >= 2 ? a.first : a.second;
        const int leaf_b = b.first >= 2 ? b.first : b.second;
        if (center_a == center_b) {
          type = "same_center_spokes";
        } else if (leaf_a == leaf_b) {
          type = "opposite_same_leaf";
        } else {
          type = "opposite_distinct_leaves";
        }
      }
      ++orbit_sizes[type];
    }
  }
  const std::map<std::string, int> expected_orbits = {
      {"center_spoke", 12},
      {"same_center_spokes", 30},
      {"opposite_same_leaf", 6},
      {"opposite_distinct_leaves", 30}};
  if (orbit_sizes != expected_orbits) {
    std::cerr << "deletion-pair orbit classification failed\n";
    return 8;
  }

  const auto started = std::chrono::steady_clock::now();
  std::uint64_t total_instances = 0;
  std::uint64_t direct_conflicts = 0;
  std::uint64_t solved_unsat = 0;
  std::uint64_t total_nodes = 0;
  std::uint64_t maximum_nodes = 0;

  for (const auto& representative : representatives) {
    std::set<int> first_set(fixed_double_star.begin(),
                            fixed_double_star.end());
    first_set.erase(representative.first_deleted);
    first_set.erase(representative.second_deleted);

    std::uint64_t rep_instances = 0;
    std::uint64_t rep_conflicts = 0;
    std::uint64_t rep_unsat = 0;
    std::uint64_t rep_nodes = 0;
    std::uint64_t rep_maximum_nodes = 0;

    for (const auto& second_core : cores) {
      const auto& second_double_star = double_stars[second_core];
      for (int i = 0; i < 13; ++i) {
        for (int j = i + 1; j < 13; ++j) {
          ++total_instances;
          ++rep_instances;
          std::set<int> second_set(second_double_star.begin(),
                                   second_double_star.end());
          second_set.erase(second_double_star[i]);
          second_set.erase(second_double_star[j]);

          std::map<int, int> forced;
          bool direct_conflict = false;
          for (int edge = 0; edge < 210; ++edge) {
            const auto [u, v] = edges[edge];
            if (first_set.count(u) != 0 && first_set.count(v) != 0) {
              forced[edge] = 1;
            }
            if (second_set.count(u) != 0 && second_set.count(v) != 0) {
              const auto found = forced.find(edge);
              if (found != forced.end() && found->second == 1) {
                direct_conflict = true;
                break;
              }
              forced[edge] = 0;
            }
          }
          if (direct_conflict) {
            ++direct_conflicts;
            ++rep_conflicts;
            continue;
          }

          const bool satisfiable = solver.Solve(forced);
          total_nodes += solver.nodes();
          rep_nodes += solver.nodes();
          maximum_nodes = std::max(maximum_nodes, solver.nodes());
          rep_maximum_nodes = std::max(rep_maximum_nodes, solver.nodes());
          if (satisfiable) {
            std::cerr << "counterexample found for " << representative.name
                      << " and second core {" << second_core.first << ','
                      << second_core.second << "}\n";
            return 2;
          }
          ++solved_unsat;
          ++rep_unsat;
        }
      }
    }

    std::cout << representative.name << " instances=" << rep_instances
              << " direct_conflicts=" << rep_conflicts
              << " solved_unsat=" << rep_unsat << " nodes=" << rep_nodes
              << " max_nodes=" << rep_maximum_nodes << '\n';
  }

  const auto finished = std::chrono::steady_clock::now();
  const double seconds =
      std::chrono::duration<double>(finished - started).count();
  std::cout << "TOTAL instances=" << total_instances
            << " direct_conflicts=" << direct_conflicts
            << " solved_unsat=" << solved_unsat
            << " nodes=" << total_nodes << " max_nodes=" << maximum_nodes
            << " seconds=" << seconds << '\n';

  if (total_instances != 8736 || direct_conflicts != 6596 ||
      solved_unsat != 2140 || direct_conflicts + solved_unsat != total_instances) {
    std::cerr << "unexpected exhaustive-search totals\n";
    return 9;
  }
  return 0;
}
