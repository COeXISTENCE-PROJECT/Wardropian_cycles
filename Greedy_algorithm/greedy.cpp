#include <bits/stdc++.h>
using namespace std;
#define ll long long
#define debug 0
class Route
{
public:
    ll Q;
    double time;
    ll id;
    Route(ll id, ll Q, double time)
    {
        this->id = id;
        this->Q = Q;
        this->time = time;
    }

    Route()
    {
        this->Q = 0;
        this->time = 0;
    }

    friend bool operator<(const Route &a, const Route &b)
    {
        // the route with the highest time is first
        return a.time > b.time;
    }
};

class Agent
{
public:
    ll id;
    double sum_time;
    Agent(ll id)
    {
        this->id = id;
        this->sum_time = 0;
    }

    Agent()
    {
        this->id = 0;
        this->sum_time = 0;
    }

    void add_time(double time)
    {
        if (debug)
            cout << "time adder: agent " << this->id << " of time " << this->sum_time << " increases by " << time << endl;
        this->sum_time += time;
        this->sum_time = round(this->sum_time * 1000) / 1000;
    }

    friend bool operator<(const Agent &a, const Agent &b)
    {
        // the agent with the highest sum of times is first
        return a.sum_time < b.sum_time;
    }
};

vector<Agent> agents;
vector<Route> routes;
vector<vector<ll>> history; // history of the agents' positions day by day
ll Q; // number of agents
ll K; // number of routes

void read_input()
{
    cin >> Q;
    cin >> K;
    agents.clear();
    agents.resize(Q);
    routes.clear();
    routes.resize(K);

    ll i = 0;
    for (int j = 0; j < K; j++)
    {
        ll q;
        double t;
        cin >> q >> t;
        routes[j] = Route(j,q, t);
    }
    for (int i = 0; i < Q; i++)
    {
        agents[i] = Agent(i);
    }

    history.clear();

    if (debug)
    {
        cout << "Agents: " << endl;
        for (int i = 0; i < agents.size(); i++)
        {
            cout << agents[i].id << " ";
        }
        cout << endl;

        cout << "Routes: " << endl;
        for (int i = 0; i < routes.size(); i++)
        {
            cout << routes[i].Q << " " << routes[i].time << endl;
        }
    }
}

void prepare_routes()
{
    double min_time = min_element(routes.begin(), routes.end(), [](Route a, Route b) { return a.time < b.time; })->time;
    for (auto &route : routes)
    {
        route.time -= min_time;
    }

    sort(routes.begin(), routes.end());

    if (debug)
    {
        cout << "Sorted routes: " << endl;
        for (int i = 0; i < routes.size(); i++)
        {
            cout << routes[i].Q << " " << routes[i].time << endl;
        }
    }
}

vector<ll> assign_routes(vector<Route> routes, vector<Agent> agents)
{
    // given sorted routes and agents, assign the routes to the agents in a greedy way
    // i.e assign the best route to q agents with the highest sum of times
    // returns the vector of the assigned routes for each agent
    
    vector<ll> assigned_routes(agents.size(), 0);
    ll idx = 0;
    for (int i=0;i < routes.size(); i++)
    {
        for (int j=0;j<routes[i].Q;j++)
        {
            assigned_routes[idx] = i;
            idx++;
        }
    }

    return assigned_routes;
}

void simulation_step()
{
    vector<ll> assigned_routes = assign_routes(routes, agents);


    for (int i = 0; i < agents.size(); i++)
    {
        agents[i].add_time(routes[assigned_routes[i]].time);
    }

    vector<ll> agent_history(agents.size(), 0);

    for (int i = 0; i < agents.size(); i++)
    {
        agent_history[agents[i].id] = assigned_routes[i];
    }

    history.push_back(agent_history);

    sort(agents.begin(), agents.end()); // sort the agents by the sum of times
   
}

void step_stats()
{
    cout << "Agent stats: " << endl;
    for (int i = 0; i < agents.size(); i++)
    {
        cout << "Agent " << agents[i].id << " has time " << agents[i].sum_time << endl;
    }
}

bool check_conv(double eps, ll cntr)
{
    double min_time = min_element(agents.begin(), agents.end(), [](Agent a, Agent b) { return a.sum_time < b.sum_time; })->sum_time;
    double max_time = max_element(agents.begin(), agents.end(), [](Agent a, Agent b) { return a.sum_time < b.sum_time; })->sum_time;
    double max_diff = max_time - min_time;
    if (max_diff > eps)
    {
        cout << "Not converged yet! Max diff: " << max_diff << endl;
        return false;
    }
    cout << "Converged in " << cntr << " steps!" << endl;
    cout << "Agents time: " << endl;
    for (int i = 0; i < agents.size(); i++)
    {
        cout << agents[i].sum_time << " ";
    }
    return true;
}

void simul_stats()
{
    cout << "Simulation stats: " << endl;
    
    vector<vector<ll>> agent_stats(agents.size(), vector<ll>(routes.size(), 0));

    for (int i = 0; i < history.size(); i++)
    {
        for (int j = 0; j < history[i].size(); j++)
        {
            agent_stats[j][history[i][j]]++;
        }
    }

    for (int i = 0; i < agent_stats.size(); i++)
    {
        cout << "Agent " << i << " stats: " << endl;
        for (int j = 0; j < agent_stats[i].size(); j++)
        {
            cout << agent_stats[i][j] << " ";
        }
        cout << endl;
    }
}

int main()
{
    read_input();

    prepare_routes();
    /*
    This greedy algorithm is a simple implementation of the Wardropian principle.
    The algorithm is not guaranteed to converge to the optimal solution, but it is a good starting point.
    What it does is to simulate road assignment to agents in a greedy way - at each step, the algorithm assigns the best route to the agent that has the highest sum of times.
    The algorithm stops when the convergence condition is met, i.e., when the difference between the sum of times of the best and the second best agents is less than eps.
    */

    bool converge = false;
    ll cntr = 0;
    while (!converge)
    {
        cntr++;
        simulation_step();

        if (cntr % 100 == 0)
        {
            step_stats();
        }

        if(check_conv(0, cntr))
        {
            break;
        }

        if (cntr > 10000)
        {
            cout << "Did not converge!" << endl;
            break;
        }
    }
    
    simul_stats();
}