"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Plus, Search, User, Clock } from "lucide-react";
import { useLanguageStore } from "@/store/language-store";
import { formatDate } from "@/lib/utils";
import { t } from "@/lib/i18n";
import apiClient from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";

export default function ForumPage() {
  const { currentLanguage } = useLanguageStore();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = React.useState("");
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [newPost, setNewPost] = React.useState({ title: "", content: "", category: "" });

  const { data: posts, isLoading } = useQuery({
    queryKey: ["forum-posts", currentLanguage],
    queryFn: async () => {
      const response = await apiClient.forum.getPosts();
      return response.data;
    },
  });

  const createPostMutation = useMutation({
    mutationFn: async (data: { title: string; content: string; category?: string }) => {
      const response = await apiClient.forum.createPost(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["forum-posts"] });
      setShowCreateForm(false);
      setNewPost({ title: "", content: "", category: "" });
    },
  });

  const handleCreatePost = () => {
    if (newPost.title && newPost.content) {
      createPostMutation.mutate(newPost);
    }
  };

  const filteredPosts = posts?.filter((post: any) =>
    post.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    post.content?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Community Forum</h1>
          <p className="text-muted-foreground">
            Share experiences, ask questions, and connect with fellow travelers
          </p>
        </div>
        {user && (
          <Button onClick={() => setShowCreateForm(!showCreateForm)}>
            <Plus className="mr-2 h-4 w-4" />
            New Post
          </Button>
        )}
      </div>

      {showCreateForm && user && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Create New Post</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Post Title"
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
            />
            <Textarea
              placeholder="Post Content"
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              rows={5}
            />
            <Input
              placeholder="Category (optional)"
              value={newPost.category}
              onChange={(e) => setNewPost({ ...newPost, category: e.target.value })}
            />
            <div className="flex gap-2">
              <Button onClick={handleCreatePost} disabled={createPostMutation.isPending}>
                {createPostMutation.isPending ? "Posting..." : "Post"}
              </Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search posts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPosts.map((post: any) => (
            <Card key={post.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{post.title}</CardTitle>
                    {post.category && (
                      <Badge variant="secondary" className="mb-2">
                        {post.category}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4 line-clamp-3">
                  {post.content}
                </p>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center space-x-4">
                    {post.author && (
                      <div className="flex items-center space-x-1">
                        <User className="h-4 w-4" />
                        <span>{post.author}</span>
                      </div>
                    )}
                    {post.created_at && (
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{formatDate(post.created_at)}</span>
                      </div>
                    )}
                    {post.comment_count !== undefined && (
                      <div className="flex items-center space-x-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{post.comment_count} comments</span>
                      </div>
                    )}
                  </div>
                  <Link href={`/forum/${post.id}`}>
                    <Button variant="ghost" size="sm">
                      Read More
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}






