// Independent exact NAE solver. No SAT-library dependency.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>
using namespace std;
struct Solver {
 int n; vector<vector<int>> cs; uint64_t nodes=0;
 bool dfs(vector<int> a){
  ++nodes; bool changed=true;
  while(changed){
   changed=false;
   for(auto const& c:cs){
    bool seen0=false,seen1=false;int unknown=0,last=-1;
    for(int x:c){if(a[x]<0){++unknown;last=x;} else if(a[x])seen1=true;else seen0=true;}
    if(seen0&&seen1)continue;
    if(!unknown)return false;
    if(unknown==1){a[last]=seen1?0:1;changed=true;}
   }
  }
  vector<int> score(n,0);bool done=true;
  for(auto const&c:cs){bool z=false,o=false;int u=0;
   for(int x:c){if(a[x]==0)z=true;else if(a[x]==1)o=true;else ++u;}
   if(z&&o)continue;
   done=false;int w=1<<(6-u);
   for(int x:c)if(a[x]<0)score[x]+=w;
  }
  if(done)return true;
  int x=int(max_element(score.begin(),score.end())-score.begin());
  if(a[x]>=0){cerr<<"Branching invariant failed\n";exit(3);}
  a[x]=0;if(dfs(a))return true;a[x]=1;return dfs(a);
 }
 bool solve(){return dfs(vector<int>(n,-1));}
};
int main(){
 Solver sat{3,{{0,1,2}}};if(!sat.solve())return 2;
 Solver unsat{3,{{0,1},{1,2},{0,2}}};if(unsat.solve())return 2;
 vector<pair<int,int>> v;for(int a=0;a<7;++a)for(int b=a+1;b<7;++b)v.emplace_back(a,b);
 auto dis=[&](int a,int b){auto x=v[a],y=v[b];return x.first!=y.first&&x.first!=y.second&&x.second!=y.first&&x.second!=y.second;};
 int e[21][21];for(auto &r:e)fill(begin(r),end(r),-1);int ne=0;
 for(int i=0;i<21;++i)for(int j=i+1;j<21;++j)if(dis(i,j))e[i][j]=e[j][i]=ne++;
 vector<int>s{2,3,4,5,6,8,9,10,11,12,13,15,17,18,19};
 vector<vector<int>>cs;array<int,2>count{0,0};
 for(int k=0;k<2;++k){int len=k==0?3:5;
  auto walk=[&](auto&&self,vector<int>p)->void{
   if(int(p.size())==len){if(e[p.back()][p[0]]>=0&&p[1]<p.back()){
    vector<int>c;for(int i=0;i<len;++i)c.push_back(e[p[i]][p[(i+1)%len]]);cs.push_back(c);++count[k];}return;}
   for(int x:s)if(x>p[0]&&e[p.back()][x]>=0&&find(p.begin(),p.end(),x)==p.end()){
    auto q=p;q.push_back(x);self(self,q);}
  };
  for(int x:s)walk(walk,vector<int>{x});
 }
 if(v.size()!=21||ne!=105||cs.size()!=1144){cerr<<"Graph totals incorrect\n";return 2;}
 cout<<"21 vertices; 105 edges; "<<count[0]<<" triangles; "<<count[1]<<" pentagons\n";
 Solver solver{ne,cs};auto start=chrono::steady_clock::now();bool r=solver.solve();
 cout<<(r?"SAT":"UNSAT")<<"; "<<solver.nodes<<" exact search nodes; "<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<" seconds\n";
 return r?1:0;
}
