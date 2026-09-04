// Exact sharpness witness for the independence-number obstruction in KG(8,2).
//
// The hard-coded 210-bit string colors the lexicographically ordered Kneser
// edges. This program reconstructs KG(8,2), checks all 420 triangles, and
// computes the independence number of both color graphs by a complete
// include/exclude branch-and-bound search.
//
// Expected terminal line:
//   SHARP triangle_free=1 alpha0=10 alpha1=10 nodes0=411 nodes1=267

#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace {

struct MaximumIndependentSet {
  std::array<std::uint32_t, 28> adjacency{};
  int best = 0;
  std::uint32_t witness = 0;
  std::uint64_t nodes = 0;

  void search(std::uint32_t candidates, int size, std::uint32_t chosen) {
    ++nodes;
    if (size + std::popcount(candidates) <= best) return;
    if (candidates == 0) {
      if (size > best) {
        best = size;
        witness = chosen;
      }
      return;
    }

    // Branch on a maximum-degree candidate to make the exact search small.
    int vertex = -1;
    int degree = -1;
    std::uint32_t remaining = candidates;
    while (remaining != 0) {
      const int candidate = std::countr_zero(remaining);
      remaining &= remaining - 1;
      const int candidate_degree =
          std::popcount(adjacency[candidate] & candidates);
      if (candidate_degree > degree) {
        degree = candidate_degree;
        vertex = candidate;
      }
    }

    const std::uint32_t vertex_bit = std::uint32_t{1} << vertex;

    // Include the vertex, deleting its closed neighborhood.
    search(candidates & ~vertex_bit & ~adjacency[vertex], size + 1,
           chosen | vertex_bit);
    // Exclude the vertex.
    search(candidates & ~vertex_bit, size, chosen);
  }
};

}  // namespace

int main() {
  std::vector<std::pair<int, int>> ground_pairs;
  for (int i = 0; i < 8; ++i) {
    for (int j = i + 1; j < 8; ++j) ground_pairs.push_back({i, j});
  }

  const auto disjoint = [&](int a, int b) {
    const auto [x, y] = ground_pairs[a];
    const auto [u, v] = ground_pairs[b];
    return x != u && x != v && y != u && y != v;
  };

  std::vector<std::pair<int, int>> kneser_edges;
  std::array<std::array<int, 28>, 28> edge_id{};
  for (auto& row : edge_id) row.fill(-1);
  for (int i = 0; i < 28; ++i) {
    for (int j = i + 1; j < 28; ++j) {
      if (disjoint(i, j)) {
        edge_id[i][j] = edge_id[j][i] =
            static_cast<int>(kneser_edges.size());
        kneser_edges.push_back({i, j});
      }
    }
  }

  // true/1 and false/0 are the two color graphs.
  const std::string coloring =
      "1110111011000100001100110101110001100110101110000011111111100001"
      "1001101110100000111111110110010101101100110011110111001111011111"
      "1111111001011011111110110100111011010001100101010000011110011000"
      "00000100111110000001";

  if (ground_pairs.size() != 28 || kneser_edges.size() != 210 ||
      coloring.size() != 210) {
    return 2;
  }

  int triangle_count = 0;
  int monochromatic_triangles = 0;
  for (int a = 0; a < 28; ++a) {
    for (int b = a + 1; b < 28; ++b) {
      for (int c = b + 1; c < 28; ++c) {
        if (!disjoint(a, b) || !disjoint(a, c) || !disjoint(b, c)) continue;
        ++triangle_count;
        const char ab = coloring[edge_id[a][b]];
        const char ac = coloring[edge_id[a][c]];
        const char bc = coloring[edge_id[b][c]];
        if (ab == ac && ac == bc) ++monochromatic_triangles;
      }
    }
  }
  if (triangle_count != 420 || monochromatic_triangles != 0) return 3;

  std::array<MaximumIndependentSet, 2> solvers;
  for (int edge = 0; edge < 210; ++edge) {
    const int color = coloring[edge] - '0';
    if (color != 0 && color != 1) return 4;
    const auto [u, v] = kneser_edges[edge];
    solvers[color].adjacency[u] |= std::uint32_t{1} << v;
    solvers[color].adjacency[v] |= std::uint32_t{1} << u;
  }

  const std::uint32_t all_vertices = (std::uint32_t{1} << 28) - 1;
  for (auto& solver : solvers) solver.search(all_vertices, 0, 0);

  // The exact branch ordering above makes these node counts deterministic.
  std::cout << "SHARP triangle_free=1 alpha0=" << solvers[0].best
            << " alpha1=" << solvers[1].best
            << " nodes0=" << solvers[0].nodes
            << " nodes1=" << solvers[1].nodes << "\n";
  std::cout << "witness0=" << solvers[0].witness
            << " witness1=" << solvers[1].witness << "\n";

  return (solvers[0].best == 10 && solvers[1].best == 10 &&
          solvers[0].nodes == 411 && solvers[1].nodes == 267)
             ? 0
             : 5;
}
