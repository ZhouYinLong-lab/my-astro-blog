import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updated: z.coerce.date().optional(),
    image: z.string().optional(),
    badge: z.string().optional(),
    draft: z.boolean().default(false),
    categories: z
      .array(z.string())
      .refine((items: string[]) => new Set(items).size === items.length, {
        message: "categories must be unique",
      })
      .optional(),
    tags: z
      .array(z.string())
      .refine((items: string[]) => new Set(items).size === items.length, {
        message: "tags must be unique",
      })
      .optional(),
  }).catchall(z.any()), // 👉 终极魔法：接收并放行任何未来自定义的字段！
});

export const collections = { blog };