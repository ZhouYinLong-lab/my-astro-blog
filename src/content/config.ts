import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z
    .object({
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
      featured: z.boolean().optional(),
      workSection: z.enum(["case-study", "experiment"]).optional(),
      bgImage: z.string().optional(),
      lang: z.string().optional(),
      author: z.string().optional(),
      canonicalURL: z.string().optional(),
      link: z.string().optional(),
      project: z
        .object({
          order: z.number().int().positive(),
          role: z.string(),
          challenge: z.string(),
          decision: z.string(),
          outcome: z.string(),
          source: z.string().url(),
          demo: z.string().url().optional(),
          metric: z.string(),
          metricLabel: z.string(),
          metricImage: z.string().optional(),
        })
        .optional(),
    })
    // catchall intentionally omitted - all frontmatter fields must be explicitly defined
});

export const collections = { blog };
