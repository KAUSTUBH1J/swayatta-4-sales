import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "./../../components/Layout/Layout";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444"];

const UserDashboardPage = () => {
  const [chartData, setChartData] = useState(null);

  // Static chart data (abhi ke liye)
  useEffect(() => {
    setChartData({
      roles_distribution: [
        { name: "Admin", count: 4 },
        { name: "Manager", count: 10 },
        { name: "Employee", count: 60 },
        { name: "Intern", count: 8 },
      ],
      departments_distribution: [
        { name: "HR", count: 12 },
        { name: "IT", count: 25 },
        { name: "Finance", count: 10 },
        { name: "Sales", count: 20 },
      ],
      regions_distribution: [
        { name: "North", count: 15 },
        { name: "South", count: 22 },
        { name: "East", count: 10 },
        { name: "West", count: 18 },
      ],
      users_distribution: [
        { name: "Active", count: 100 },
        { name: "Inactive", count: 20 },
      ],
    });
  }, []);

  const kpis = [
    { key: "users", title: "Total Users", value: 120, color: "bg-blue-500", icon: "👤", link: "/users", footer: "Manage users" },
    { key: "roles", title: "Active Roles", value: 8, color: "bg-green-500", icon: "🛡️", link: "/roles", footer: "View roles" },
    { key: "departments", title: "Departments", value: 12, color: "bg-purple-500", icon: "🏢", link: "/departments", footer: "Organize departments" },
    { key: "regions", title: "Regions", value: 6, color: "bg-yellow-500", icon: "🌍", link: "/regions", footer: "Explore regions" },
  ];

  // Top 5 recents
  const topRecentData = {
    users: [
      { id: 1, name: "Harsh", email: "harsh@example.com", created_at: "2025-08-20" },
      { id: 2, name: "Anil", email: "anil@example.com", created_at: "2025-08-19" },
    ],
    roles: [
      { id: 1, name: "Admin", created_at: "2025-08-20" },
      { id: 2, name: "Manager", created_at: "2025-08-18" },
    ],
    departments: [
      { id: 1, name: "IT", created_at: "2025-08-19" },
      { id: 2, name: "HR", created_at: "2025-08-17" },
    ],
    regions: [
      { id: 1, name: "North", created_at: "2025-08-16" },
      { id: 2, name: "South", created_at: "2025-08-15" },
    ],
  };

  const recentActivities = [
    { id: 1, user: "Harsh", action: "added Region", time: "2 mins ago", color: "bg-green-500" },
    { id: 2, user: "Anil", action: "updated Role", time: "15 mins ago", color: "bg-blue-500" },
    { id: 3, user: "Sneha", action: "deleted Department", time: "1 hr ago", color: "bg-red-500" },
    { id: 4, user: "Shashank", action: "created User", time: "2 hrs ago", color: "bg-purple-500" },
  ];

  return (
    <Layout>
      <div className="space-y-10">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            User Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Overview of key metrics
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpis.map((kpi) => (
            <Link
              key={kpi.key}
              to={kpi.link}
              className="block p-6 bg-white dark:bg-gray-800 rounded-xl shadow hover:shadow-lg transform hover:-translate-y-1 transition"
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white text-lg ${kpi.color}`}>
                {kpi.icon}
              </div>
              <div className="mt-4 text-3xl font-extrabold text-gray-900 dark:text-gray-100">
                {kpi.value}
              </div>
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {kpi.title}
              </div>
              <div className="mt-4 text-xs text-blue-600 dark:text-blue-400 font-medium">
                {kpi.footer} →
              </div>
            </Link>
          ))}
        </div>

        {/* Charts */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Employees Distribution
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {chartData &&
              Object.entries(chartData).map(([key, data]) => (
                <div key={key}>
                  <h3 className="text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    By {key.replace("_distribution", "").toUpperCase()}
                  </h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={data}
                        dataKey="count"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {data.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ))}
          </div>
        </div>

        {/* Top 5 Recent Data */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(topRecentData).map(([entity, items]) => (
            <div key={entity} className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Recent {entity.charAt(0).toUpperCase() + entity.slice(1)}
                </h2>
                <Link to={`/${entity}`} className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
                  View all →
                </Link>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {items.map((item) => (
                  <div key={item.id} className="py-3 flex justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {item.name}
                      </p>
                      {item.email && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{item.email}</p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">{item.created_at}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Recent Activity Timeline */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Recent Activity
            </h2>
            <Link to="/activity-logs" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              View all →
            </Link>
          </div>
          <div className="relative pl-4">
            <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
            <ul className="space-y-6">
              {recentActivities.map((activity) => (
                <li key={activity.id} className="relative flex items-start">
                  <span className={`absolute left-[-6px] w-3 h-3 rounded-full ${activity.color} mt-1`}></span>
                  <div className="ml-6">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      <span className="font-medium">{activity.user}</span> {activity.action}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{activity.time}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default UserDashboardPage;
