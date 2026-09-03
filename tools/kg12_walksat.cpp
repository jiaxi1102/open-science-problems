#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

using Triple = std::array<int, 3>;
using Edge = std::array<int, 2>;

static std::vector<Triple> choose3(int n) {
  std::vector<Triple> out;
  for (int a = 0; a < n; ++a)
    for (int b = a + 1; b < n; ++b)
      for (int c = b + 1; c < n; ++c) out.push_back({a, b, c});
  return out;
}

static uint16_t mask_of(const Triple &t) {
  return static_cast<uint16_t>((1u << t[0]) | (1u << t[1]) | (1u << t[2]));
}

static uint64_t pair_key(int a, int b) {
  if (a > b) std::swap(a, b);
  return (static_cast<uint64_t>(static_cast<uint32_t>(a)) << 32) |
         static_cast<uint32_t>(b);
}

struct Instance {
  std::vector<Triple> vertices;
  std::vector<uint16_t> masks;
  std::vector<Edge> edges;
  std::unordered_map<uint64_t, int> edge_id;
  std::vector<Triple> triangles;
  std::vector<std::vector<int>> incident;
  std::vector<int8_t> fixed;
};

static Instance build_instance(const std::string &branch) {
  Instance g;
  g.vertices = choose3(12);
  g.masks.reserve(g.vertices.size());
  std::unordered_map<uint16_t, int> vertex_id;
  for (int i = 0; i < static_cast<int>(g.vertices.size()); ++i) {
    uint16_t mask = mask_of(g.vertices[i]);
    g.masks.push_back(mask);
    vertex_id[mask] = i;
  }

  for (int i = 0; i < static_cast<int>(g.vertices.size()); ++i) {
    for (int j = i + 1; j < static_cast<int>(g.vertices.size()); ++j) {
      if ((g.masks[i] & g.masks[j]) == 0) {
        int id = static_cast<int>(g.edges.size());
        g.edges.push_back({i, j});
        g.edge_id[pair_key(i, j)] = id;
      }
    }
  }

  for (int i = 0; i < static_cast<int>(g.vertices.size()); ++i) {
    for (int j = i + 1; j < static_cast<int>(g.vertices.size()); ++j) {
      if (g.masks[i] & g.masks[j]) continue;
      for (int k = j + 1; k < static_cast<int>(g.vertices.size()); ++k) {
        if ((g.masks[i] & g.masks[k]) || (g.masks[j] & g.masks[k])) continue;
        g.triangles.push_back({g.edge_id.at(pair_key(i, j)),
                               g.edge_id.at(pair_key(i, k)),
                               g.edge_id.at(pair_key(j, k))});
      }
    }
  }
  if (g.vertices.size() != 220 || g.edges.size() != 9240 ||
      g.triangles.size() != 61600) {
    throw std::runtime_error("unexpected KG(12,3) counts");
  }

  g.incident.assign(g.edges.size(), {});
  for (int t = 0; t < static_cast<int>(g.triangles.size()); ++t)
    for (int e : g.triangles[t]) g.incident[e].push_back(t);
  for (const auto &rows : g.incident)
    if (rows.size() != 20) throw std::runtime_error("edge triangle degree != 20");

  g.fixed.assign(g.edges.size(), -1);
  auto vid = [&](int a, int b, int c) {
    return vertex_id.at(static_cast<uint16_t>((1u << a) | (1u << b) | (1u << c)));
  };
  std::array<int, 4> block = {vid(0, 1, 2), vid(3, 4, 5), vid(6, 7, 8),
                              vid(9, 10, 11)};
  std::array<const char *, 6> names = {"AB", "AC", "AD", "BC", "BD", "CD"};
  std::array<std::array<int, 2>, 6> pairs = {
      std::array<int, 2>{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
  for (int q = 0; q < 6; ++q) {
    std::string name(names[q]);
    bool red = false;
    if (branch == "matching") red = (name == "AB" || name == "CD");
    else if (branch == "path") red = (name == "AB" || name == "BD" || name == "CD");
    else throw std::runtime_error("branch must be matching or path");
    int e = g.edge_id.at(pair_key(block[pairs[q][0]], block[pairs[q][1]]));
    g.fixed[e] = red ? 1 : 0;
  }
  return g;
}

struct Search {
  const Instance &g;
  std::mt19937_64 rng;
  std::vector<uint8_t> value;
  std::vector<uint8_t> sum;
  std::vector<int> weight;
  std::vector<int> bad;
  std::vector<int> bad_pos;
  std::vector<uint8_t> best_value;
  int best_bad;

  explicit Search(const Instance &instance, uint64_t seed)
      : g(instance), rng(seed), value(g.edges.size()), sum(g.triangles.size()),
        weight(g.triangles.size(), 1), bad_pos(g.triangles.size(), -1),
        best_bad(static_cast<int>(g.triangles.size()) + 1) {}

  bool is_bad(int t) const { return sum[t] == 0 || sum[t] == 3; }

  void add_bad(int t) {
    if (bad_pos[t] >= 0) return;
    bad_pos[t] = static_cast<int>(bad.size());
    bad.push_back(t);
  }

  void remove_bad(int t) {
    int pos = bad_pos[t];
    if (pos < 0) return;
    int last = bad.back();
    bad[pos] = last;
    bad_pos[last] = pos;
    bad.pop_back();
    bad_pos[t] = -1;
  }

  void initialize() {
    std::uniform_int_distribution<int> bit(0, 1);
    for (int e = 0; e < static_cast<int>(value.size()); ++e)
      value[e] = g.fixed[e] >= 0 ? static_cast<uint8_t>(g.fixed[e])
                                 : static_cast<uint8_t>(bit(rng));
    bad.clear();
    std::fill(bad_pos.begin(), bad_pos.end(), -1);
    for (int t = 0; t < static_cast<int>(g.triangles.size()); ++t) {
      sum[t] = static_cast<uint8_t>(value[g.triangles[t][0]] +
                                    value[g.triangles[t][1]] +
                                    value[g.triangles[t][2]]);
      if (is_bad(t)) add_bad(t);
    }
    if (static_cast<int>(bad.size()) < best_bad) {
      best_bad = static_cast<int>(bad.size());
      best_value = value;
    }
  }

  int weighted_gain(int e) const {
    int gain = 0;
    for (int t : g.incident[e]) {
      bool old_bad = is_bad(t);
      int next = static_cast<int>(sum[t]) + (value[e] ? -1 : 1);
      bool new_bad = next == 0 || next == 3;
      if (old_bad && !new_bad) gain += weight[t];
      if (!old_bad && new_bad) gain -= weight[t];
    }
    return gain;
  }

  void flip(int e) {
    uint8_t old = value[e];
    for (int t : g.incident[e]) {
      bool was_bad = is_bad(t);
      sum[t] = static_cast<uint8_t>(static_cast<int>(sum[t]) + (old ? -1 : 1));
      bool now_bad = is_bad(t);
      if (was_bad && !now_bad) remove_bad(t);
      else if (!was_bad && now_bad) add_bad(t);
    }
    value[e] ^= 1;
    if (static_cast<int>(bad.size()) < best_bad) {
      best_bad = static_cast<int>(bad.size());
      best_value = value;
    }
  }

  bool run(double seconds, int restart_steps) {
    using clock = std::chrono::steady_clock;
    auto deadline = clock::now() + std::chrono::duration<double>(seconds);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    long long step = 0;
    long long last_improvement = 0;
    int recorded_best = best_bad;

    while (clock::now() < deadline) {
      if (bad.empty()) return true;
      if (step > 0 && step % restart_steps == 0) {
        initialize();
        last_improvement = step;
      }

      int t = bad[static_cast<size_t>(rng() % bad.size())];
      std::array<int, 3> candidate = g.triangles[t];
      int chosen = -1;
      int best_gain = -1000000000;
      for (int e : candidate) {
        if (g.fixed[e] >= 0) continue;
        int gain = weighted_gain(e);
        if (gain > best_gain || (gain == best_gain && (rng() & 1))) {
          best_gain = gain;
          chosen = e;
        }
      }
      if (chosen < 0) {
        for (int x : bad) ++weight[x];
        initialize();
        ++step;
        continue;
      }

      // Focused random walk helps escape plateaus; greed otherwise.
      if (unit(rng) < 0.18) {
        std::vector<int> free_vars;
        for (int e : candidate)
          if (g.fixed[e] < 0) free_vars.push_back(e);
        chosen = free_vars[static_cast<size_t>(rng() % free_vars.size())];
      }
      flip(chosen);
      ++step;

      if (best_bad < recorded_best) {
        recorded_best = best_bad;
        last_improvement = step;
        std::cerr << "best=" << best_bad << " step=" << step << "\n";
      }
      if (step - last_improvement > 25000) {
        for (int x : bad) ++weight[x];
        last_improvement = step;
      }
      if (step % 1000000 == 0) {
        long long total = std::accumulate(weight.begin(), weight.end(), 0LL);
        if (total > 20LL * static_cast<long long>(weight.size())) {
          for (int &w : weight) w = 1 + w / 2;
        }
      }
    }
    return bad.empty();
  }
};

static void write_model(const std::string &path, const std::vector<uint8_t> &value) {
  std::ofstream out(path);
  out << "s SATISFIABLE\n";
  int on_line = 0;
  out << "v ";
  for (int i = 0; i < static_cast<int>(value.size()); ++i) {
    out << (value[i] ? i + 1 : -(i + 1)) << ' ';
    if (++on_line == 20 && i + 1 < static_cast<int>(value.size())) {
      out << "0\nv ";
      on_line = 0;
    }
  }
  out << "0\n";
}

int main(int argc, char **argv) {
  if (argc < 6) {
    std::cerr << "usage: kg12_walksat BRANCH SEED SECONDS RESTART_STEPS OUTPUT\n";
    return 2;
  }
  std::string branch(argv[1]);
  uint64_t seed = std::stoull(argv[2]);
  double seconds = std::stod(argv[3]);
  int restart_steps = std::stoi(argv[4]);
  std::string output(argv[5]);

  Instance g = build_instance(branch);
  Search search(g, seed);
  search.initialize();
  bool solved = search.run(seconds, restart_steps);
  std::cerr << "final_best=" << search.best_bad << "\n";
  if (solved || search.best_bad == 0) {
    if (!solved) search.value = search.best_value;
    write_model(output, search.value);
    return 10;
  }
  std::ofstream best(output + ".best");
  best << "best_bad " << search.best_bad << "\n";
  return 0;
}
