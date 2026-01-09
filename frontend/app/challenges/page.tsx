"use client";

import * as React from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Target, Award, Users, CheckCircle2 } from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";

export default function ChallengesPage() {
  const { currentLanguage } = useLanguageStore();
  const { user } = useAuthStore();

  const { data: challenges, isLoading } = useQuery({
    queryKey: ["challenges", currentLanguage],
    queryFn: async () => {
      const response = await apiClient.challenges.list();
      return response.data;
    },
  });

  const { data: myProgress } = useQuery({
    queryKey: ["challenges-progress"],
    queryFn: async () => {
      const response = await apiClient.challenges.getMyProgress();
      return response.data;
    },
    enabled: !!user,
  });

  const { data: leaderboard } = useQuery({
    queryKey: ["challenges-leaderboard"],
    queryFn: async () => {
      const response = await apiClient.challenges.getLeaderboard();
      return response.data;
    },
  });

  const completeChallengeMutation = useMutation({
    mutationFn: async (challengeId: string) => {
      const response = await apiClient.challenges.checkIn(challengeId, {});
      return response.data;
    },
  });

  const completedChallengeIds = new Set(
    myProgress?.filter((p: any) => p.completed).map((p: any) => p.challenge_id) || []
  );

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Travel Challenges</h1>
        <p className="text-muted-foreground">
          Complete challenges to earn badges and climb the leaderboard
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {challenges?.map((challenge: any) => {
                const isCompleted = completedChallengeIds.has(challenge.id);
                return (
                  <Card key={challenge.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Target className="h-5 w-5 text-primary" />
                            <CardTitle>{challenge.title}</CardTitle>
                            {isCompleted && (
                              <Badge variant="default" className="bg-green-500">
                                <CheckCircle2 className="mr-1 h-3 w-3" />
                                Completed
                              </Badge>
                            )}
                          </div>
                          <CardDescription>{challenge.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          {challenge.points && (
                            <div className="flex items-center space-x-1">
                              <Award className="h-4 w-4 text-yellow-500" />
                              <span className="text-sm font-medium">{challenge.points} points</span>
                            </div>
                          )}
                          {challenge.difficulty && (
                            <Badge variant="outline">{challenge.difficulty}</Badge>
                          )}
                        </div>
                        {user && !isCompleted && (
                          <Button
                            onClick={() => completeChallengeMutation.mutate(challenge.id)}
                            disabled={completeChallengeMutation.isPending}
                          >
                            {completeChallengeMutation.isPending ? "Completing..." : "Complete Challenge"}
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        <div className="space-y-6">
          {user && myProgress && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Trophy className="h-5 w-5" />
                  <span>My Progress</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Completed</span>
                    <span className="font-semibold">
                      {myProgress.filter((p: any) => p.completed).length} / {myProgress.length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Total Points</span>
                    <span className="font-semibold">
                      {myProgress.reduce((sum: number, p: any) => sum + (p.points || 0), 0)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {leaderboard && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Leaderboard</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {leaderboard.slice(0, 10).map((entry: any, index: number) => (
                    <div key={entry.user_id} className="flex items-center justify-between py-2 border-b last:border-0">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-muted-foreground w-6">#{index + 1}</span>
                        <span className="text-sm">{entry.username || "Anonymous"}</span>
                      </div>
                      <span className="font-semibold">{entry.points || 0} pts</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}






