// Select already authorized server data. Business rules and matching live in FastAPI.
export function getTeamActivities(data, teamId) {
  const team = data.teams.find((item) => item.id === teamId);
  if (!team?.projectId) return [];
  return data.scheduleActivities
    .filter((item) => item.teamId === teamId && item.projectId === team.projectId)
    .map((item) => ({ ...item, plannedStart: item.plannedStartTime ?? item.plannedStart, plannedEnd: item.plannedEndTime ?? item.plannedEnd }));
}
