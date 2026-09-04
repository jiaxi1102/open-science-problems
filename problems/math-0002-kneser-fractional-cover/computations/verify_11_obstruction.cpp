#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <utility>
#include <vector>

using namespace std;

namespace {

struct NAE3Solver {
  int variableCount;
  vector<array<int, 3>> clauses;
  vector<vector<int>> occurrences;
  array<int8_t, 210> value{};
  vector<int> trail;
  uint64_t nodes = 0;

  NAE3Solver(int n, vector<array<int, 3>> cs)
      : variableCount(n), clauses(move(cs)), occurrences(n) {
    for (int ci = 0; ci < static_cast<int>(clauses.size()); ++ci) {
      for (int v : clauses[ci]) occurrences[v].push_back(ci);
    }
  }

  bool assign(int v, int x, deque<int>& queue) {
    if (value[v] != -1) return value[v] == x;
    value[v] = static_cast<int8_t>(x);
    trail.push_back(v);
    queue.push_back(v);
    return true;
  }

  bool propagate(deque<int>& queue) {
    while (!queue.empty()) {
      int changed = queue.front();
      queue.pop_front();
      for (int ci : occurrences[changed]) {
        int zero = 0, one = 0, unset = 0, lastUnset = -1;
        for (int v : clauses[ci]) {
          if (value[v] == -1) {
            ++unset;
            lastUnset = v;
          } else if (value[v] == 0) {
            ++zero;
          } else {
            ++one;
          }
        }
        if (unset == 0) {
          if (zero == 3 || one == 3) return false;
        } else if (unset == 1) {
          if (zero == 2 && !assign(lastUnset, 1, queue)) return false;
          if (one == 2 && !assign(lastUnset, 0, queue)) return false;
        }
      }
    }
    return true;
  }

  int chooseVariable() const {
    int best = -1;
    int bestScore = -1;
    for (int v = 0; v < variableCount; ++v) {
      if (value[v] != -1) continue;
      int score = 0;
      for (int ci : occurrences[v]) {
        int zero = 0, one = 0, unset = 0;
        for (int w : clauses[ci]) {
          if (value[w] == -1) ++unset;
          else if (value[w] == 0) ++zero;
          else ++one;
        }
        if (!(zero && one)) score += 5 - unset;
      }
      if (score > bestScore) {
        bestScore = score;
        best = v;
      }
    }
    return best;
  }

  bool dfs() {
    ++nodes;
    int v = chooseVariable();
    if (v < 0) return true;
    const int mark = static_cast<int>(trail.size());
    for (int x = 0; x <= 1; ++x) {
      deque<int> queue;
      if (assign(v, x, queue) && propagate(queue) && dfs()) return true;
      while (static_cast<int>(trail.size()) > mark) {
        value[trail.back()] = -1;
        trail.pop_back();
      }
    }
    return false;
  }

  bool solve(const vector<pair<int, int>>& forced) {
    value.fill(-1);
    trail.clear();
    nodes = 0;
    deque<int> queue;
    for (auto [v, x] : forced) {
      if (!assign(v, x, queue)) return false;
    }
    return propagate(queue) && dfs();
  }
};

template <class Callback>
void combinationsOf(const vector<int>& source, int need, Callback callback) {
  vector<int> chosen;
  function<void(int, int)> visit = [&](int start, int left) {
    if (left == 0) {
      callback(chosen);
      return;
    }
    for (int i = start; i <= static_cast<int>(source.size()) - left; ++i) {
      chosen.push_back(source[i]);
      visit(i + 1, left - 1);
      chosen.pop_back();
    }
  };
  visit(0, need);
}

}  // namespace

int main() {
  const auto startTime = chrono::steady_clock::now();

  vector<pair<int, int>> vertices;
  for (int i = 0; i < 8; ++i) {
    for (int j = i + 1; j < 8; ++j) vertices.push_back({i, j});
  }
  map<pair<int, int>, int> vertexId;
  for (int i = 0; i < 28; ++i) vertexId[vertices[i]] = i;

  auto disjoint = [&](int a, int b) {
    auto A = vertices[a];
    auto B = vertices[b];
    return A.first != B.first && A.first != B.second &&
           A.second != B.first && A.second != B.second;
  };

  vector<pair<int, int>> kneserEdges;
  map<pair<int, int>, int> edgeId;
  for (int i = 0; i < 28; ++i) {
    for (int j = i + 1; j < 28; ++j) {
      if (disjoint(i, j)) {
        edgeId[{i, j}] = static_cast<int>(kneserEdges.size());
        kneserEdges.push_back({i, j});
      }
    }
  }

  vector<array<int, 3>> triangles;
  for (int a = 0; a < 28; ++a) {
    for (int b = a + 1; b < 28; ++b) {
      for (int c = b + 1; c < 28; ++c) {
        if (disjoint(a, b) && disjoint(a, c) && disjoint(b, c)) {
          triangles.push_back({edgeId[{a, b}], edgeId[{a, c}], edgeId[{b, c}]});
        }
      }
    }
  }

  vector<vector<int>> doubleStars;
  for (auto [x, y] : vertices) {
    vector<int> core;
    for (int i = 0; i < 28; ++i) {
      auto e = vertices[i];
      if (e.first == x || e.second == x || e.first == y || e.second == y) {
        core.push_back(i);
      }
    }
    if (core.size() != 13) return 2;
    doubleStars.push_back(core);
  }

  vector<vector<int>> allA;
  combinationsOf(doubleStars[0], 11, [&](const vector<int>& s) { allA.push_back(s); });
  if (allA.size() != 78) return 3;

  // Compute the four orbits of 11-subsets of D_{01} under the full stabilizer
  // of {0,1}: S_2 x S_6. This is checked, not assumed.
  vector<array<int, 28>> stabilizer;
  vector<int> tail = {2, 3, 4, 5, 6, 7};
  do {
    for (int swap = 0; swap < 2; ++swap) {
      array<int, 8> pointPerm{};
      pointPerm[0] = swap ? 1 : 0;
      pointPerm[1] = swap ? 0 : 1;
      for (int i = 0; i < 6; ++i) pointPerm[i + 2] = tail[i];
      array<int, 28> edgePerm{};
      for (int i = 0; i < 28; ++i) {
        int x = pointPerm[vertices[i].first];
        int y = pointPerm[vertices[i].second];
        if (x > y) swap(x, y);
        edgePerm[i] = vertexId[{x, y}];
      }
      stabilizer.push_back(edgePerm);
    }
  } while (next_permutation(tail.begin(), tail.end()));
  if (stabilizer.size() != 1440) return 4;

  map<vector<int>, int> aIndex;
  for (int i = 0; i < static_cast<int>(allA.size()); ++i) aIndex[allA[i]] = i;
  set<int> unseen;
  for (int i = 0; i < 78; ++i) unseen.insert(i);
  vector<int> representatives;
  vector<int> orbitSizes;
  while (!unseen.empty()) {
    int representative = *unseen.begin();
    set<int> orbit;
    for (const auto& perm : stabilizer) {
      vector<int> image;
      for (int v : allA[representative]) image.push_back(perm[v]);
      sort(image.begin(), image.end());
      auto it = aIndex.find(image);
      if (it == aIndex.end()) return 5;
      orbit.insert(it->second);
    }
    representatives.push_back(representative);
    orbitSizes.push_back(static_cast<int>(orbit.size()));
    for (int i : orbit) unseen.erase(i);
  }
  sort(orbitSizes.begin(), orbitSizes.end());
  if (representatives.size() != 4 || orbitSizes != vector<int>({6, 12, 30, 30})) return 6;

  set<vector<int>> uniqueB;
  for (const auto& core : doubleStars) {
    combinationsOf(core, 11, [&](const vector<int>& s) { uniqueB.insert(s); });
  }
  vector<vector<int>> allB(uniqueB.begin(), uniqueB.end());
  if (allB.size() != 2184) return 7;

  auto internalKneserEdges = [&](const vector<int>& set) {
    vector<int> result;
    for (int i = 0; i < static_cast<int>(set.size()); ++i) {
      for (int j = i + 1; j < static_cast<int>(set.size()); ++j) {
        int a = set[i], b = set[j];
        if (a > b) swap(a, b);
        auto it = edgeId.find({a, b});
        if (it != edgeId.end()) result.push_back(it->second);
      }
    }
    sort(result.begin(), result.end());
    result.erase(unique(result.begin(), result.end()), result.end());
    return result;
  };

  vector<vector<int>> aEdges;
  vector<vector<int>> bEdges;
  for (int i : representatives) aEdges.push_back(internalKneserEdges(allA[i]));
  for (const auto& b : allB) bEdges.push_back(internalKneserEdges(b));

  NAE3Solver solver(static_cast<int>(kneserEdges.size()), triangles);
  uint64_t tested = 0;
  uint64_t immediateOverlap = 0;
  uint64_t searchNodes = 0;

  for (int ai = 0; ai < static_cast<int>(representatives.size()); ++ai) {
    vector<char> blueForced(kneserEdges.size(), 0);
    for (int e : aEdges[ai]) blueForced[e] = 1;
    for (int bi = 0; bi < static_cast<int>(allB.size()); ++bi) {
      ++tested;
      vector<pair<int, int>> forced;
      for (int e : aEdges[ai]) forced.push_back({e, 1});
      bool conflict = false;
      for (int e : bEdges[bi]) {
        if (blueForced[e]) {
          conflict = true;
          break;
        }
        forced.push_back({e, 0});
      }
      if (conflict) {
        ++immediateOverlap;
        continue;
      }
      if (solver.solve(forced)) {
        cerr << "Unexpected satisfying colouring for orbit " << ai
             << " and B choice " << bi << '\n';
        return 8;
      }
      searchNodes += solver.nodes;
    }
  }

  const double seconds = chrono::duration<double>(chrono::steady_clock::now() - startTime).count();
  cout << "UNSAT"
       << " vertices=28 kneser_edges=" << kneserEdges.size()
       << " triangles=" << triangles.size()
       << " A_total=" << allA.size()
       << " A_orbits=" << representatives.size()
       << " B_total=" << allB.size()
       << " tested_orbit_pairs=" << tested
       << " immediate_overlap=" << immediateOverlap
       << " dpll_nodes=" << searchNodes
       << " seconds=" << seconds << '\n';
  return 0;
}
